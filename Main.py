import gradio as gr
import logging
from modules.UI_manager import UI

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=f'UI_render.{__name__}')

UI_manager = UI()

with gr.Blocks() as demo:
    gr.Markdown("# *WL Analysis*")
    with gr.Tab("Report filter"):
        with gr.Row():
            unique_years,unique_type,unique_region = UI_manager.available_filters()
            year = gr.Dropdown(choices=unique_years, interactive=True, label="Year")
            type = gr.Dropdown(choices=unique_type, interactive=True, label="Type")
            region = gr.Dropdown(choices=unique_region, interactive=True, label="Region")
            customer = gr.Text(label="Customer")
            product = gr.Text(label="Products")

            filter_bttn = gr.Button("Filter")
        with gr.Row():
            text_search = gr.Text(label="Search by query:", placeholder="Give me documents in America...")    
            with gr.Column():
                query_btn = gr.Button("Search")
                message = gr.Text(container=False,interactive=False)
        with gr.Row():
            file_list = gr.List(label="Documents available")
            
        with gr.Row():
            new_files = gr.File(file_count='multiple')
        with gr.Row():
            new_file_bttn = gr.Button("Upload files")
            ok_message = gr.Label()

    with gr.Tab("Chat"):
        gr.ChatInterface(
                fn=UI_manager.get_client_analysis, 
                title= 'OCI Client chat lite',
                theme='ocean',
                chatbot=gr.Chatbot(height=500, placeholder='OCI chat',type='messages',render_markdown=True),
                textbox=gr.Textbox(placeholder='Ask me anything...',container=True),
                type="messages",
                additional_inputs=[
                    gr.Textbox(placeholder='Answer me in a song...',label='System Instructions'),
                ]
            )            

    filter_bttn.click(
        UI_manager.manage_filter,
        inputs=[year,type,region,customer,product],
        outputs=[file_list]
    )

    query_btn.click(
        UI_manager.get_client_filter,
        inputs=[text_search],
        outputs=[file_list,message]
    )

    new_file_bttn.click(
        UI_manager.manage_files,
        inputs=[new_files],
        outputs=[ok_message]
    )

if __name__=='__main__':
    demo.launch(show_api=False)