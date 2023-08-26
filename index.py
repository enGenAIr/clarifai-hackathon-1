import streamlit as st
from PIL import Image, ImageFilter
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
import os
import dotenv

dotenv.load_dotenv()
class ImageStoryGenerator:
    def __init__(self):
        self.USER_ID = os.getenv("USER_ID")
        self.PAT = os.getenv("PAT")
        self.APP_ID = os.getenv("APP_ID")
        self.WORKFLOW_ID_IMAGE = os.getenv("WORKFLOW_ID_IMAGE")
        self.WORKFLOW_ID_TEXT = os.getenv("WORKFLOW_ID_TEXT")
        self.channel = ClarifaiChannel.get_grpc_channel()
        self.stub = service_pb2_grpc.V2Stub(self.channel)

    def process_image(self, uploaded_file):
        if not os.path.exists("uploaded_images"):
            os.makedirs("uploaded_images")
        
        image = Image.open(uploaded_file)
        image_name = uploaded_file.name
        image_name_without_extension = image_name.split(".")[0]
        image.save(f'uploaded_images/{image_name_without_extension}.jpg')

        return image

    def apply_filter(self, image, filter_option):
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
        else:
            return image

    def generate_tags(self, image_path):
        file_bytes = None
        with open(image_path, "rb") as f:
            file_bytes = f.read()

        post_workflow_results_response = self.stub.PostWorkflowResults(
            service_pb2.PostWorkflowResultsRequest(
                user_app_id=resources_pb2.UserAppIDSet(user_id=self.USER_ID, app_id=self.APP_ID),
                workflow_id=self.WORKFLOW_ID_IMAGE,
                inputs=[
                    resources_pb2.Input(
                        data=resources_pb2.Data(
                            image=resources_pb2.Image(base64=file_bytes)
                        )
                    )
                ]
            ),
            metadata=(('authorization', 'Key ' + self.PAT),)
        )

        tags = []
        if file_bytes and post_workflow_results_response.status.code == status_code_pb2.SUCCESS:
            tags = [concept.name for concept in post_workflow_results_response.results[0].outputs[0].data.concepts]
        
        return tags

    def generate_text(self, tags, text_option):
        tags_str = ' '.join(tags)

        if text_option == 'Story':
            raw_text = f'write a personalized poem (4-lines) maximum about: {tags}'
        elif text_option == 'Poem':
            raw_text = f'write a personalized (4-lines) maximum about: {tags_str}'
        else:
            raw_text = ""

        return raw_text

    def generate_story(self, raw_text):
        post_workflow_results_response_text = self.stub.PostWorkflowResults(
            service_pb2.PostWorkflowResultsRequest(
                user_app_id=resources_pb2.UserAppIDSet(user_id=self.USER_ID, app_id=self.APP_ID),
                workflow_id=self.WORKFLOW_ID_TEXT,
                inputs=[
                    resources_pb2.Input(
                        data=resources_pb2.Data(
                            text=resources_pb2.Text(raw=raw_text)
                        )
                    )
                ]
            ),
            metadata=(('authorization', 'Key ' + self.PAT),)
        )

        generated_text = ""
        if raw_text and post_workflow_results_response_text.status.code == status_code_pb2.SUCCESS:
            generated_text = post_workflow_results_response_text.results[0].outputs[0].data.text.raw
            generated_text = generated_text.split(":", 1)[-1].strip()

        return generated_text
def main():
    st.title('Your Personalized Image Story')
    uploaded_file = st.file_uploader("Choose an image...", type="jpg")

    if uploaded_file is not None:
        generator = ImageStoryGenerator()
        
        image = generator.process_image(uploaded_file)
        st.image(image, caption='Uploaded Image.', use_column_width=True)

        filter_option = st.selectbox(
            'Which filter would you like to apply?',
            ('Original', 'BLUR', 'CONTOUR', 'EMBOSS', 'FIND_EDGES', 'SHARPEN')
        )

        text_option = st.selectbox(
            'What kind of text would you like to generate?',
            ('Story', 'Poem')
        )

        generate_button = st.button("Generate")
        if generate_button:
            if filter_option != 'Original':
                image = generator.apply_filter(image, filter_option)

            tags = generator.generate_tags(f'uploaded_images/{uploaded_file.name.split(".")[0]}.jpg')
            raw_text = generator.generate_text(tags, text_option)

            if raw_text:
                generated_text = generator.generate_story(raw_text)
                st.image(image, caption=generated_text, use_column_width=True)


if __name__ == "__main__":
    main()
