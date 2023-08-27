## python -m streamlit run final_code.py

import streamlit as st
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageOps
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
import os
import textwrap
from dotenv import load_dotenv
from ImageBorder import ImageBorder
import re

# Load environment variables
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
            'SHARPEN': ImageFilter.SHARPEN,
            'SMOOTH': ImageFilter.SMOOTH,
            'DETAIL': ImageFilter.DETAIL,
            'EDGE_ENHANCE': ImageFilter.EDGE_ENHANCE,
            'EDGE_ENHANCE_MORE': ImageFilter.EDGE_ENHANCE_MORE,
            'GAUSSIAN_BLUR': ImageFilter.GaussianBlur(radius=2),
            'MEDIAN_FILTER': ImageFilter.MedianFilter(size=3),
            'MAX_FILTER': ImageFilter.MaxFilter(size=3),
            'MIN_FILTER': ImageFilter.MinFilter(size=3),
            'SEPIA': 'SEPIA',
            'GRAYSCALE': 'GRAYSCALE'
        }

        if filter_option in filters:
            if filter_option == 'SEPIA':
                img = self.image.convert("RGB")
                pixels = img.getdata()
                new_pixels = []
                for pixel in pixels:
                    r, g, b = pixel
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    new_pixels.append((tr, tg, tb))
                img.putdata(new_pixels)
                self.image = img

            elif filter_option == 'GRAYSCALE':
                grayscale = ImageOps.grayscale(self.image)
                self.image = grayscale.convert("RGB")
                
            else:
                self.image = self.image.filter(filters[filter_option])
    
    def apply_border(self, border_type, text=None):
        if border_type == 'Polaroids':
            self.image = ImageBorder.basic_polaroid(self.image)
        elif border_type == 'Vintage Frame':
            self.image = ImageBorder.vintage_frame(self.image)
        elif border_type == 'Filmstrip Border':
            self.image = ImageBorder.filmstrip_border(self.image, text)
        elif border_type == 'Grunge Border':
            self.image = ImageBorder.grunge_border(self.image, text)
        elif border_type == 'Framed Border':
            self.image = ImageBorder.framed_border(self.image, text)


    def resize(self, width, height):
        img = self.image.resize((width, height))
        self.image = img

    def add_text(self, text, position_option, font_color, bg_color=None, font_size=20):
        draw = ImageDraw.Draw(self.image)
        try:
            font = ImageFont.truetype("Arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
            st.warning("Using default font. Font size will not be adjustable.")

        wrapped_text = textwrap.fill(text, width=30)
        text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position_map = {
        'Top Left': (10, 10),
        'Top Center': ((self.image.width - text_width) // 2, 10),
        'Top Right': (self.image.width - text_width - 10, 10),
        'Bottom Left': (10, self.image.height - text_height - 10),
        'Bottom Center': ((self.image.width - text_width) // 2, self.image.height - text_height - 10),
        'Bottom Right': (self.image.width - text_width - 10, self.image.height - text_height - 10),
        'Center': ((self.image.width - text_width) // 2, (self.image.height - text_height) // 2)
        }

        position = position_map[position_option]

        if bg_color:
            draw.rectangle([position, (position[0] + text_width, position[1] + text_height)], fill=bg_color)
        
        draw.text(position, wrapped_text, fill=font_color, font=font)

    
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

        text_data = response.results[0].outputs[0].data.text.raw

        # Try splitting using colon
        split_result = text_data.split(":", 1)
        if len(split_result) > 1:
            text_data = split_result[-1].strip()

        text_data = re.search(r'"([^"]+)"', text_data)
        if text_data:
            text_data = text_data.group(1)
        else:
            st.warning("No inverted data found in the response.")
            return ""
        
        return text_data
    

def main():
    st.title('PoeticaPic')
    st.write('PoeticaPic is a tool for creating beautiful, unique and stylish images using Poetry and Art.')
    st.sidebar.header('Settings')

    uploaded_file = st.file_uploader("Choose an image...", type="jpg")

    if uploaded_file:
        image = Image.open(uploaded_file)

        if not os.path.exists("uploaded_images"):
            os.makedirs("uploaded_images")

        image_name = uploaded_file.name
        image_name_without_extension = image_name.split(".")[0]
        image_path = f'uploaded_images/{image_name_without_extension}.jpg'
        image.save(image_path)

        processor = ImageProcessor(image)

        # Filter Selection in Sidebar
        filter_option = st.sidebar.selectbox(
            'Apply Filter:',
            ('Original', 'BLUR', 'CONTOUR', 'DETAIL', 'EDGE_ENHANCE', 'EDGE_ENHANCE_MORE',
             'EMBOSS', 'SHARPEN', 'SMOOTH', 'SMOOTH_MORE', 'GAUSSIAN_BLUR', 'MEDIAN_FILTER', 'MAX_FILTER', 'MIN_FILTER','SEPIA','GRAYSCALE')
        )
        processor.apply_filter(filter_option)

        # Default values for width and height
        default_width = 400
        default_height = 400

        width = st.sidebar.slider("Select Image Width:", 100, 800, default_width)
        height = st.sidebar.slider("Select Image Height:", 100, 800, default_height)
        processor.resize(width, height)
        

        border_option = st.sidebar.selectbox(
            'Do You Wanna Apply Border?',
            ('Original', 'Polaroids',
             'Vintage Frame', 'Filmstrip Border', 'Grunge Border', 'Framed Border' )
        )

        if border_option != 'Original':
            processor.apply_border(border_option)
        

        st.image(processor.image, caption='Preview')

        # Text Options in Sidebar
        st.sidebar.subheader("Text Options")
        text_option = st.sidebar.selectbox(
            'Text Type:',
            ('Phrase', 'Quote')
        )
        text_position = st.sidebar.selectbox(
            'Text Position:',
            ('Top Left', 'Top Right', 'Top Center','Bottom Left', 'Bottom Right','Bottom Center' ,'Center')
        )
        max_font_size = min(image.width, image.height) // 30
        font_size = st.sidebar.slider('Font Size:', 8, max_font_size, 15)
        font_color = st.sidebar.color_picker('Font Color:', '#ffffff')
        bg_color_option = st.sidebar.checkbox('Background Color?')
        bg_color = st.sidebar.color_picker('Background Color:', '#000000') if bg_color_option else None

        

        if st.button('Generate Text & Apply'):
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

                st.image(modified_image_path, caption='Final Image')
                with open(modified_image_path, 'rb') as f:
                    modified_image_bytes = f.read()
                st.download_button('Download Modified Image', data=modified_image_bytes, file_name='modified_image.jpg')
            else:
                st.error("Failed to generate text. Please try again.")

if __name__ == "__main__":
    main()
