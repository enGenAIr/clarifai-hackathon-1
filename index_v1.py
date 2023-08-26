## Command to run /// python -m streamlit run git_code.py   

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

uploaded_file = st.file_uploader("Choose an image...", type="jpg")

image = Image

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)
    image_name = uploaded_file.name
    image_name_without_extension = image_name.split(".")[0]
    image.save(f'uploaded_images/{image_name_without_extension}.jpg')


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

file_bytes = None
if uploaded_file:
    with open(f'uploaded_images/{image_name_without_extension}.jpg', "rb") as f:
        file_bytes = f.read()

# Call the Clarifai workflow
post_workflow_results_response = stub.PostWorkflowResults(
    service_pb2.PostWorkflowResultsRequest(
        user_app_id=resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID),
        workflow_id=WORKFLOW_ID_IMAGE,
        inputs=[
            resources_pb2.Input(
                data=resources_pb2.Data(
                    image=resources_pb2.Image(base64=file_bytes
                    )
                )
            )
        ]
    ),
    metadata=(('authorization', 'Key ' + PAT),)
)

tags=""
if file_bytes:
    if post_workflow_results_response.status.code != status_code_pb2.SUCCESS:
        st.write("Post workflow results failed, status: " + post_workflow_results_response.status.description)
    else:
        tags = [concept.name for concept in post_workflow_results_response.results[0].outputs[0].data.concepts]

tags_str = None
RAW_TEXT = None
if tags != "":
    # Convert the tags to a single string
    tags_str =  tags[0] + ' '+tags[1]


    ################ USER FLOW CHOICES ###########
    if text_option == 'Story':
        RAW_TEXT = f'generate me a Story for "{tags_str}"'
    elif text_option == 'Poem':
        RAW_TEXT = f'generate me a Poem for "{tags_str}"'
        
    print(RAW_TEXT)
    #################################################



# Call the Clarifai workflow for text-to-text generation
post_workflow_results_response_text = stub.PostWorkflowResults(
    service_pb2.PostWorkflowResultsRequest(
        user_app_id=resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID),
        workflow_id=WORKFLOW_ID_TEXT,
        inputs=[
            resources_pb2.Input(
                data=resources_pb2.Data(
                    text=resources_pb2.Text(raw=RAW_TEXT)
                )
            )
        ]
    ),
    metadata=(('authorization', 'Key ' + PAT),)
)
if RAW_TEXT:
    # Check the status of the response
    if post_workflow_results_response_text.status.code != status_code_pb2.SUCCESS:
        st.write("Post workflow results failed, status: " + post_workflow_results_response_text.status.description)
    else:
        # Extract the generated text
        generated_text = post_workflow_results_response_text.results[0].outputs[0].data.text.raw
        text_after_colon = generated_text.split(":", 1)[-1].strip()
        # Display the image with the generated text
        st.image(image, caption=text_after_colon)


