import streamlit as st
from PIL import Image, ImageFilter
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
import io
import os
from dotenv import load_dotenv
# Clarifai constants
load_dotenv()

USER_ID = os.getenv("USER_ID")
PAT = os.getenv("PAT")
APP_ID = os.getenv("APP_ID")
WORKFLOW_ID_IMAGE = os.getenv("WORKFLOW_ID_IMAGE")
WORKFLOW_ID_TEXT = os.getenv("WORKFLOW_ID_TEXT")
metadata = (('authorization', 'Key ' + PAT),)

class ClarifaiAPI:
    def __init__(self):
        self.channel = ClarifaiChannel.get_grpc_channel()
        self.stub = service_pb2_grpc.V2Stub(self.channel)

    def post_workflow_results_image(self, img_str):
        response = self.stub.PostWorkflowResults(
            service_pb2.PostWorkflowResultsRequest(
                user_app_id=resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID),
                workflow_id=WORKFLOW_ID_IMAGE,
                inputs=[
                    resources_pb2.Input(
                        data=resources_pb2.Data(
                            image=resources_pb2.Image(base64=img_str)
                        )
                    )
                ]
            ),
            metadata=metadata
        )
        return response

    def post_workflow_results_text(self, tags_str):
        response = self.stub.PostWorkflowResults(
            service_pb2.PostWorkflowResultsRequest(
                user_app_id=resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID),
                workflow_id=WORKFLOW_ID_TEXT,
                inputs=[
                    resources_pb2.Input(
                        data=resources_pb2.Data(
                            text=resources_pb2.Text(raw=tags_str)
                        )
                    )
                ]
            ),
            metadata=metadata
        )
        return response

def apply_filter(image, filter_option):
    if filter_option == 'BLUR':
        return image.filter(ImageFilter.BLUR)
    elif filter_option == 'CONTOUR':
        return image.filter(ImageFilter.CONTOUR)
    elif filter_option == 'EMBOSS':
        return image.filter(ImageFilter.EMBOSS)
    elif filter_option == 'FIND_EDGES':
        return image.filter(ImageFilter.FIND_EDGES)
    elif filter_option == 'SHARPEN':
        return image.filter(ImageFilter.SHARPEN)
    return image

def main():
    st.title('Your Personalized Image Story')

    clarifai_api = ClarifaiAPI()

    with st.form(key='my_form'):
        uploaded_file = st.file_uploader("Choose an image...", type="jpeg")
        submit_button = st.form_submit_button(label='Submit')

    filter_option = st.selectbox(
        'Which filter would you like to apply?',
        ('Original', 'BLUR', 'CONTOUR', 'EMBOSS', 'FIND_EDGES', 'SHARPEN')
    )

    if submit_button and uploaded_file is not None:
        image = Image.open(uploaded_file)
        image = apply_filter(image, filter_option)

        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()

        post_response_image = clarifai_api.post_workflow_results_image(img_bytes)
        if post_response_image.status.code != status_code_pb2.SUCCESS:
            st.write("Post model outputs failed, status: " + post_response_image.status.description)
        else:
            output = post_response_image.outputs[0]
            predictions = [concept.name for concept in output.data.concepts]
            st.title(predictions[0], ",", predictions[1])

            tags_str = ' '.join(predictions)

            post_response_text = clarifai_api.post_workflow_results_text(tags_str)
            if post_response_text.status.code != status_code_pb2.SUCCESS:
                st.write("Post workflow results failed, status: " + post_response_text.status.description)
            else:
                generated_text = post_response_text.results[0].outputs[0].data.text.raw
                st.image(image, caption=generated_text)

if __name__ == "__main__":
    main()
