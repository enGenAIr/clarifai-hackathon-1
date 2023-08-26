### python -m streamlit run index_v1.py

import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from PIL.ImageDraw import ImageDraw
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
import os
from dotenv import load_dotenv
from ImageBorder import ImageBorder

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

    # def apply_filter(self, filter_option):
    #     filters = {
    #         'Blur': ImageFilter.BLUR,
    #         "Black & White": ImageFilter.UnsharpMask(radius=2, percent=150),
    #         "Dramatic": ImageEnhance.Contrast(self.image),
    #     }
    #     if filter_option in filters:
    #         self.image = self.image.filter(filters[filter_option])

    def apply_filter(self, filter_option):
        self.image = self.return_filter(filter_option)


    def return_filter(self, filter_name):
        if filter_name == "Original":
            return self.image
        elif filter_name == "Black & White":
            grayscale = ImageOps.grayscale(self.image)
            return grayscale.convert("RGB")
        elif filter_name == "Dramatic":
            enhancer = ImageEnhance.Contrast(self.image)
            return enhancer.enhance(1.5)
        elif filter_name == "Vintage":
            vintage_filter = self.image.convert("RGB")

            # Apply Gaussian blur
            vintage_filter = vintage_filter.filter(ImageFilter.GaussianBlur(radius=2))

            # Apply color adjustments for the retro effect
            enhancer = ImageEnhance.Color(vintage_filter)
            vintage_filter = enhancer.enhance(0.7)  # Reduce color saturation

            enhancer = ImageEnhance.Brightness(vintage_filter)
            vintage_filter = enhancer.enhance(0.8)  # Reduce brightness

            enhancer = ImageEnhance.Contrast(vintage_filter)
            vintage_filter = enhancer.enhance(1.2)  # Increase contrast

            # Apply color tint (brownish tone)
            for y in range(vintage_filter.height):
                for x in range(vintage_filter.width):
                    r, g, b = vintage_filter.getpixel((x, y))
                    r = min(255, int(r * 1.2))
                    g = min(255, int(g * 0.9))
                    b = min(255, int(b * 0.7))
                    vintage_filter.putpixel((x, y), (r, g, b))

            return vintage_filter
        elif filter_name == "Sharp":
            return self.image.filter(ImageFilter.UnsharpMask(radius=2, percent=150))
        elif filter_name == "Cool":
            return ImageEnhance.Color(self.image).enhance(0.6)
        elif filter_name == "Warm":
            enhancer = ImageEnhance.Color(self.image)
            return enhancer.enhance(1.5)
        elif filter_name == "Blur":
            return self.image.filter(ImageFilter.GaussianBlur(radius=3))
        else:
            raise ValueError("Filter not implemented!")
    def resize(self, width, height):
        self.image = self.image.resize((width, height))

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
            ('Original', 'Blur', 'Black & White', 'Dramatic', 'Vintage', 'Sharp', 'Cool', 'Warm')
        )
        if filter_option != 'Original':
            processor.apply_filter(filter_option)

        # Separate Resizing Option
        resize_option = st.checkbox("Would you like to resize the image?")
        if resize_option:
            width = st.slider("Select Image Width:", 100, 800, 400)
            height = st.slider("Select Image Height:", 100, 800, 400)
            processor.resize(width, height)

        # Border Selection
        border_option = st.selectbox(
            'Do You Wanna Apply Border?',
            ('Original', 'Polaroids',
             'Vintage Frame', 'Filmstrip Border', 'Grunge Border', 'Framed Border' )
        )

        if border_option != 'Original':
            processor.apply_border(border_option)

        # Display the final image after all modifications
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
                st.write(generated_text)

if __name__ == "__main__":
    main()
