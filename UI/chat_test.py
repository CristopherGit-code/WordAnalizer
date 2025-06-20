import logging
from modules.llm_client import Client
import gradio as gr

logger = logging.getLogger(name=f'LLM Client ------------------>')
client = Client()

def get_oci_response(prompt,message_history,system_instructions,preamble,temperature,uploaded_files):
    query = prompt['text']
    files = prompt['files'] #list with files
    return client.botConversation(query,system_instructions)

gr.ChatInterface(
    title= 'OCI Client chat lite',
    description='Chat with the model',
    theme='ocean',
    fn=get_oci_response, 
    chatbot=gr.Chatbot(height=400, placeholder='OCI chat'),
    multimodal=True, # Create different inputs
    textbox=gr.MultimodalTextbox(file_count='multiple',file_types=['image'],sources=['upload']),
    type="messages",
    additional_inputs=[
        gr.Textbox(placeholder='Answer me in a song...',label='System Instructions'),
        gr.Textbox(placeholder='Respond in less than 200 words...',label='System preamble'),
        gr.Slider(value=0.8,minimum=0,maximum=1,step=0.1,label='Temperature'),
        gr.File()
    ]
).launch()