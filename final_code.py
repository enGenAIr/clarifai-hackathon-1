### python -m streamlit run index_v1.py
import base64

import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from PIL.ImageDraw import ImageDraw
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
import os
from dotenv import load_dotenv
from ImageProcessor import ImageProcessor

# Clarifai constants
load_dotenv()

# Constants
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

    st.markdown("<h1 style='text-align: center; color: #1e88e5;'>PoeticaPic</h1>", unsafe_allow_html=True)
    st.write('PoeticaPic is a tool for creating beautiful, unique, and stylish images using Poetry and Art.')

    # Sidebar
    st.sidebar.markdown("<h3 style='color: #1e88e5; padding-bottom: 10px;'>Settings</h3>", unsafe_allow_html=True)

    uploaded_file = st.sidebar.file_uploader("Choose an image (jpg only)", type="jpg")

    if uploaded_file:
        image = Image.open(uploaded_file)

        if not os.path.exists("uploaded_images"):
            os.makedirs("uploaded_images")

        image_name = uploaded_file.name
        image_name_without_extension = image_name.split(".")[0]
        image_path = f'uploaded_images/{image_name_without_extension}.jpg'
        image.save(image_path)

        processor = ImageProcessor(image)

        # Filter Selection
        st.sidebar.markdown("<h4 style='color: #1e88e5;'>Image Filters</h4>", unsafe_allow_html=True)
        st.sidebar.write('Select from a variety of filters to enhance your image.')
        filter_option = st.sidebar.selectbox(
            'Which filter would you like to apply?',
            ('Original', 'Blur', 'Black & White', 'Vignette', 'Sepia', 'Pop Art',)
        )
        if filter_option != 'Original':
            processor.apply_filter(filter_option)

        # Resize
        st.sidebar.markdown("<h4 style='color: #1e88e5;'>Resize Image</h4>", unsafe_allow_html=True)
        default_width = 600
        default_height = 400
        width = st.sidebar.slider("Width:", 100, 800, default_width)
        height = st.sidebar.slider("Height:", 100, 800, default_height)
        processor.resize(width, height)

        # Border Selection
        st.sidebar.markdown("<h4 style='color: #1e88e5;'>Border Options</h4>", unsafe_allow_html=True)
        st.sidebar.write('Add a border to make your image stand out.')
        border_option = st.sidebar.selectbox(
            'Apply Border?',
            ('Original', 'Polaroids','Glitch Frame' ,'Wooden Frame','Cartoon Frame' , 'Pixel Frame','Filmstrip Border','Vintage Frame' , 'Bubble Frame')
        )
        if border_option != 'Original':
            processor.apply_border(border_option)

        # Text Options
        st.sidebar.markdown("<h4 style='color: #1e88e5;'>Text Options</h4>", unsafe_allow_html=True)
        text_option = st.sidebar.selectbox('Text Type:', ('Phrase', 'Quote'))
        text_position = st.sidebar.selectbox('Text Position:', ('Top Left', 'Top Right', 'Top Center', 'Bottom Left', 'Bottom Right', 'Bottom Center', 'Center'))
        max_font_size = min(image.width, image.height) // 30
        font_size = st.sidebar.slider('Font Size:', 8, max_font_size, 15)
        font_color = st.sidebar.color_picker('Font Color:', '#ffffff')
        bg_color_option = st.sidebar.checkbox('Background Color?')
        bg_color = st.sidebar.color_picker('Background Color:', '#000000') if bg_color_option else None

        st.image(processor.image, caption='Preview', use_column_width=True, clamp=True)

        if st.sidebar.button('Generate Text & Apply', key='generate'):
            api = ClarifaiAPI()
            tags = api.get_image_tags(image_path)
            if tags:
                tags_str = ' '.join(tags[:2])
                raw_text = f'generate me a tiny {text_option} for "{tags_str} must only be a few words"'
                generated_text = api.get_text(raw_text)
                processor.add_text(generated_text, text_position, font_color, bg_color)

                # Save the modified image
                modified_image_path = f'uploaded_images/{image_name_without_extension}_modified.jpg'
                processor.save(modified_image_path)

                st.image(modified_image_path, caption='Final Image', use_column_width=True)
                with open(modified_image_path, 'rb') as f:
                    modified_image_bytes = f.read()
                st.download_button('Download Modified Image', data=modified_image_bytes, file_name='modified_image.jpg', key='download')
            else:
                st.error("Failed to generate text. Please try again.")


if __name__ == "__main__":
    main()
