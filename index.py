import streamlit as st
from PIL import Image, ImageFilter
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
import base64
import io
# Clarifai constants
USER_ID = 'umar05'
PAT = '04ad0503aff5443fb2e09f6a3c74950e'
APP_ID = 'my-first-application-ryesqk'
WORKFLOW_ID_IMAGE = 'General'
WORKFLOW_ID_TEXT = 'workflow-7c8454'
st.title('Your Personalized Image Story')

uploaded_file="https://samples.clarifai.com/metro-north.jpg"
uploaded_file = st.file_uploader("Choose an image...", type="jpg")

image = Image

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)

filter_option = st.selectbox(
    'Which filter would you like to apply?',
    ('Original', 'BLUR', 'CONTOUR', 'EMBOSS', 'FIND_EDGES', 'SHARPEN')
)

text_option = st.selectbox(
    'What kind of text would you like to generate?',
    ('Story', 'Poem')
)

if filter_option == 'BLUR':
    image = image.filter(ImageFilter.BLUR)
elif filter_option == 'CONTOUR':
    image = image.filter(ImageFilter.CONTOUR)
elif filter_option == 'EMBOSS':
    image = image.filter(ImageFilter.EMBOSS)
elif filter_option == 'FIND_EDGES':
    image = image.filter(ImageFilter.FIND_EDGES)
elif filter_option == 'SHARPEN':
    image = image.filter(ImageFilter.SHARPEN)
    
channel = ClarifaiChannel.get_grpc_channel()
stub = service_pb2_grpc.V2Stub(channel)

img = image

# Create a BytesIO object
img_byte_arr = io.BytesIO()

# Save the image to the BytesIO object
img.save(fp=img_byte_arr,  format='PNG')
# Get the byte array
img_byte_arr = img_byte_arr.getvalue()


img_base64 = base64.b64encode(img_byte_arr)

# Call the Clarifai workflow
post_workflow_results_response = stub.PostWorkflowResults(
    service_pb2.PostWorkflowResultsRequest(
        user_app_id=resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID),
        workflow_id=WORKFLOW_ID_IMAGE,
        inputs=[
            resources_pb2.Input(
                data=resources_pb2.Data(
                    image=resources_pb2.Image(url="https://samples.clarifai.com/metro-north.jpg"
                    )
                )
            )
        ]
    ),
    metadata=(('authorization', 'Key ' + PAT),)
)

tags=""

if post_workflow_results_response.status.code != status_code_pb2.SUCCESS:
    st.write("Post workflow results failed, status: " + post_workflow_results_response.status.description)
else:
    tags = [concept.name for concept in post_workflow_results_response.results[0].outputs[0].data.concepts]


# Convert the tags to a single string
tags_str = ' '.join(tags)

# Call the Clarifai workflow for text-to-text generation
post_workflow_results_response_text = stub.PostWorkflowResults(
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
    metadata=(('authorization', 'Key ' + PAT),)
)

# Check the status of the response
if post_workflow_results_response_text.status.code != status_code_pb2.SUCCESS:
    st.write("Post workflow results failed, status: " + post_workflow_results_response_text.status.description)
else:
    # Extract the generated text
    generated_text = post_workflow_results_response_text.results[0].outputs[0].data.text.raw

    # Display the image with the generated text
    st.image(image, caption=generated_text)


