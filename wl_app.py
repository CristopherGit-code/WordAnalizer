import logging
import gradio as gr
from modules.UI_manager import UI

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=f'UI_render.{__name__}')

UI_manager = UI()

md_message = UI_manager.get_chat_placeholder()
welcome_message = UI_manager.get_welcome_placeholder()

with gr.Blocks() as wl_app:
    gr.Markdown("""<h1 align="center"> Win / Loss call analysis </h1>""")

    welcome = gr.Markdown(welcome_message,visible=True)
    close_btn = gr.Button("Got it!",visible=True,variant="secondary")
    
    ## Main user state for each session
    chat_init_uuid = gr.State()

    chat_instructions = gr.Textbox(placeholder='Answer in just bullet points...',label='System Instructions', render=False)

    with gr.Column(visible=False) as main_app:
        with gr.Tab("File filter"):
            with gr.Row(equal_height=True):
                with gr.Column():
                    text_search = gr.Textbox(label="Search by query:", placeholder="Give me documents in America...")
                    gr.Textbox("- Loss documents from japan.\n- Documents with product PG&E.\n- Win documents from california.\n- 2014 loss documents from us and product HERs.\n- loss document from 2023, customer: Efficiency One",label="Examples:",interactive=False,lines=5)
                with gr.Row(equal_height=True):
                    unique_years,unique_type,unique_region,unique_customer = UI_manager.available_filters()
                    year = gr.Dropdown(choices=unique_years, interactive=True, label="Year")
                    type = gr.Dropdown(choices=unique_type, interactive=True, label="Type")
                    region = gr.Dropdown(choices=unique_region, interactive=True, label="Region")
                    customer = gr.Dropdown(choices=unique_customer, interactive=True, label="Customer")
                    product = gr.Text(label="Products",placeholder="'Enter' to search")
            
            file_list = gr.List(show_label=True, show_row_numbers=True, col_count=None,headers=["Documents Found - Go to chat window"],scale=5)

            text_search.submit(
                UI_manager.get_client_filter,
                inputs=[year,type,region,customer,product, text_search, chat_init_uuid, file_list],
                outputs=[file_list]
            )

            year.change(
                UI_manager.get_client_manual_filter,
                inputs=[year,type,region,customer,product, text_search, chat_init_uuid, file_list],
                outputs=[file_list]
            )
            type.change(
                UI_manager.get_client_manual_filter,
                inputs=[year,type,region,customer,product, text_search, chat_init_uuid, file_list],
                outputs=[file_list]   
            )
            region.change(
                UI_manager.get_client_manual_filter,
                inputs=[year,type,region,customer,product, text_search, chat_init_uuid, file_list],
                outputs=[file_list]   
            )
            customer.change(
                UI_manager.get_client_manual_filter,
                inputs=[year,type,region,customer,product, text_search, chat_init_uuid, file_list],
                outputs=[file_list]   
            )
            
        with gr.Tab("Chat"):
            gr.ChatInterface(
                    fn=UI_manager.get_client_analysis, 
                    chatbot=gr.Chatbot(height=500, placeholder=md_message ,type='messages',render_markdown=True),
                    type="messages",
                    additional_inputs=[
                        chat_instructions,
                        chat_init_uuid
                    ]
                )
            
    close_btn.click(UI_manager.hide_welcome,outputs=[welcome,close_btn,main_app])

    wl_app.load(
        fn = UI_manager.load_user_session,
        inputs=[chat_init_uuid],
        outputs=[chat_init_uuid]
    )

if __name__=='__main__':
    #wl_app.queue(max_size=60).launch(max_threads=6, root_path="/wl-analysis", server_port=6100,show_api=False)
    wl_app.launch(show_api=False)