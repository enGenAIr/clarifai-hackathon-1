### python -m streamlit run index_v1.py

import streamlit as st
from PIL import Image, ImageFilter
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
import os
from dotenv import load_dotenv
# Clarifai constants
load_dotenv()

# Constants
USER_ID = os.getenv("USER_ID")
PAT = os.getenv("PAT")
APP_ID = os.getenv("APP_ID")
WORKFLOW_ID_IMAGE = os.getenv("WORKFLOW_ID_IMAGE")
WORKFLOW_ID_TEXT = os.getenv("WORKFLOW_ID_TEXT")
metadata = (('authorization', 'Key ' + PAT),)

class ImageProcessor:
    def __init__(self, image):
        self.image = image

    def apply_filter(self, filter_option):
        filters = {
            'BLUR': ImageFilter.BLUR,
            'CONTOUR': ImageFilter.CONTOUR,
            'EMBOSS': ImageFilter.EMBOSS,
            'FIND_EDGES': ImageFilter.FIND_EDGES,
            'SHARPEN': ImageFilter.SHARPEN
        }
        if filter_option in filters:
            self.image = self.image.filter(filters[filter_option])

    def resize(self, width, height):
        self.image = self.image.resize((width, height))


class ClarifaiAPI:
    def __init__(self):
        self.channel = ClarifaiChannel.get_grpc_channel()
        self.stub = service_pb2_grpc.V2Stub(self.channel)

    def get_image_tags(self, image_path):
        with open(image_path, "rb") as f:
            file_bytes = f.read()

        response = self.stub.PostWorkflowResults(
            service_pb2.PostWorkflowResultsRequest(
                user_app_id=resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID),
                workflow_id=WORKFLOW_ID_IMAGE,
                inputs=[
                    resources_pb2.Input(
                        data=resources_pb2.Data(
                            image=resources_pb2.Image(base64=file_bytes)
                        )
                    )
                ]
            ),
            metadata=metadata
        )

        if response.status.code != status_code_pb2.SUCCESS:
            st.write("Post workflow results failed, status: " + response.status.description)
            return []

        return [concept.name for concept in response.results[0].outputs[0].data.concepts]

    def get_text(self, raw_text):
        response = self.stub.PostWorkflowResults(
            service_pb2.PostWorkflowResultsRequest(
                user_app_id=resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID),
                workflow_id=WORKFLOW_ID_TEXT,
                inputs=[
                    resources_pb2.Input(
                        data=resources_pb2.Data(
                            text=resources_pb2.Text(raw=raw_text)
                        )
                    )
                ]
            ),
            metadata=metadata
        )

        if response.status.code != status_code_pb2.SUCCESS:
            st.write("Post workflow results failed, status: " + response.status.description)
            return ""

        return response.results[0].outputs[0].data.text.raw.split(":", 1)[-1].strip()


def main():
    st.title('Your Personalized Image Story')

    uploaded_file = st.file_uploader("Choose an image...", type="jpg")

    if uploaded_file:
        image = Image.open(uploaded_file)

        if not os.path.exists("uploaded_images"):
            os.makedirs("uploaded_images")

        image_name = uploaded_file.name
        image_name_without_extension = image_name.split(".")[0]
        image_path = f'uploaded_images/{image_name_without_extension}.jpg'
        image.save(image_path)  # Save the original image

        processor = ImageProcessor(image)
        
        # Filter Selection
        filter_option = st.selectbox(
            'Which filter would you like to apply?',
            ('Original', 'BLUR', 'CONTOUR', 'EMBOSS', 'FIND_EDGES', 'SHARPEN')
        )
        processor.apply_filter(filter_option)
        
        # Separate Resizing Option
        resize_option = st.checkbox("Would you like to resize the image?")
        if resize_option:
            width = st.slider("Select Image Width:", 100, 800, 400)
            height = st.slider("Select Image Height:", 100, 800, 400)
            processor.resize(width, height)
            st.image(processor.image, caption='Modified Image.')

        text_option = st.selectbox(
            'What kind of text would you like to generate?',
            ('Story', 'Poem')
        )

        if st.button('Submit'):
            api = ClarifaiAPI()
            tags = api.get_image_tags(image_path)
            if tags:
                tags_str = ' '.join(tags[:2])
                raw_text = f'generate me a {text_option} for "{tags_str}"'
                generated_text = api.get_text(raw_text)
                st.image(processor.image, caption=generated_text)


if __name__ == "__main__":
    main()
