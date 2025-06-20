import gradio as gr
from modules.llm_client import Client
from modules.db import DataBase
from modules.config import Settings
from modules.file_handler import File_handlder

settings = Settings("App.yaml")
client = Client()
db = DataBase(settings)
file_manager = File_handlder()

summary_data = ''

def get_db_response(name_list,year=2010,type=None,region=None,customer=None,product=None):
    db_query = db.build_query(name_list,year,type,region,customer,product)
    db_response = db.sort_files(db_query)
    lists = [list(group) for group in zip(*db_response)]
    return lists

def manage_filter(year,type,region,customer,product):
    global summary_data
    data_list = ['t.metadata.file_name','t.content']
    client.reset_chat() # Reset to explain the mew filters
    # TODO: fix no_bid problem
    responses = get_db_response(data_list,year,type,region,customer,product)
    if not responses:
        return ['No files found with that filter']
    else:
        summary_data = file_manager.merge_md(responses[1])
        return responses[0]

def manage_files(files):
    print(files)
    return 'Uploaded files'

def get_client_analysis(prompt,message_history,system_instructions=''):
    query = prompt + f'given the data in {summary_data}'
    fix_instructions = f'Consider the report data: {summary_data}.' + system_instructions
    return client.provide_analysis(query, fix_instructions)

def get_client_filter(prompt:str):
    r_dict = client.filter_files(prompt)
    year = r_dict[0]
    type = r_dict[1]
    region = r_dict[2]
    customer = r_dict[3]
    product = r_dict[4]
    lists = manage_filter(year,type,region,customer,product)
    message = f'Filter applied to prompt: {r_dict}'
    return lists,message

def available_filters():
    responses = get_db_response(['t.metadata.report_date','t.metadata.type','t.metadata.regions[0].region'])
    years = [int(date[:4]) for date in responses[0]]
    years.insert(0,2010)
    unique_years = sorted(set(years))

    responses[1].insert(0,"")
    unique_type = sorted(set(responses[1]))

    responses[2].insert(0,"")
    unique_region = sorted(set(responses[2]))
    return unique_years,unique_type,unique_region

with gr.Blocks() as demo:
    gr.Markdown("*WL Analysis*")
    with gr.Tab("Report filter"):
        with gr.Row():
            unique_years,unique_type,unique_region = available_filters()
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
                fn=get_client_analysis, 
                title= 'OCI Client chat lite',
                theme='ocean',
                chatbot=gr.Chatbot(height=500, placeholder='OCI chat',type='messages'),
                textbox=gr.Textbox(placeholder='Ask me anything...',container=True),
                type="messages",
                additional_inputs=[
                    gr.Textbox(placeholder='Answer me in a song...',label='System Instructions'),
                ]
            )            

    filter_bttn.click(
        manage_filter,
        inputs=[year,type,region,customer,product],
        outputs=[file_list]
    )

    query_btn.click(
        get_client_filter,
        inputs=[text_search],
        outputs=[file_list,message]
    )

    new_file_bttn.click(
        manage_files,
        inputs=[new_files],
        outputs=[ok_message]
    )

if __name__=='__main__':
    demo.launch(show_api=False)