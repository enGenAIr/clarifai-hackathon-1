## python -m streamlit run final_code.py

import streamlit as st
from PIL import Image, ImageFilter, ImageDraw,ImageFont,ImageColor
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

    def add_text(self, text, position, font_color, bg_color=None, font_size=20):
        draw = ImageDraw.Draw(self.image)
        print(font_size)
        try:
            font = ImageFont.truetype("Arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
            st.warning("Using default font. Font size will not be adjustable.")

        if bg_color:
            text_width, text_height = draw.textsize(text, font=font)
            draw.rectangle([position, (position[0] + text_width, position[1] + text_height)], fill=bg_color)
        
        draw.text(position, text, fill=font_color, font=font)

    def save(self, path):
        self.image.save(path)

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
            ('Phrase', 'Quote')
        )

        text_position = st.selectbox(
            'Where would you like the text to appear?',
            ('Top Left', 'Top Right', 'Bottom Left', 'Bottom Right', 'Center')
        )
        # Adding style options for the user
        font_size = st.slider('Choose font size:', 10, 60, 20)
        font_color = st.color_picker('Choose font color:', '#ffffff')
        bg_color_option = st.checkbox('Add background color to text?')
        bg_color = None
        if bg_color_option:
            bg_color = st.color_picker('Choose text background color:', '#000000')

        if st.button('Submit'):
            api = ClarifaiAPI()
            tags = api.get_image_tags(image_path)
            if tags:
                tags_str = ' '.join(tags[:2])
                raw_text = f'generate me a short {text_option} for "{tags_str}"'
                generated_text = api.get_text(raw_text)
                
                position_map = {
                    'Top Left': (10, 10),
                    'Top Right': (processor.image.width - 200, 10),
                    'Bottom Left': (10, processor.image.height - 30),
                    'Bottom Right': (processor.image.width - 200, processor.image.height - 30),
                    'Center': ((processor.image.width - 200) // 2, (processor.image.height - 30) // 2)
                }
                
                processor.add_text(generated_text, position_map[text_position], font_color, bg_color)

                # Save the modified image
                modified_image_path = f'uploaded_images/{image_name_without_extension}_modified.jpg'
                processor.save(modified_image_path)

                st.image(modified_image_path, caption='Image with Text.')


if __name__ == "__main__":
    main()
