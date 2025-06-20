from modules.file_handler import File_handlder
from modules.db import DataBase
from modules.llm_client import Client
from modules.config import Settings
from pathlib import Path
import json,logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name='Test_update')

# Receive word TODO: check if the document was previously updated

source_folder = Path(r'C:\Users\Cristopher Hdz\Desktop\Test\WordAnalizer\Files\Call reports')
template = r'C:\Users\Cristopher Hdz\Desktop\Test\WordAnalizer\Files\template.json'

settings = Settings('wl_analysis.yaml')
file_manager = File_handlder()
llm = Client(settings)
db = DataBase(settings)

missing = ['FYnn Loss to Silver Spring - Portland General -Dynamic Rates']

with open(template,'r') as file:
    metadata = json.load(file)

for file_path in source_folder.iterdir():
    if file_path.is_file():
        file_suffix = str(file_path.suffix)
        file_name = str(file_path.name).replace(file_suffix,'')
        if file_name in missing:
            missing.remove(file_name)
            md = file_manager.parse_file(file_path)
            md = md.replace(" ","")
            logger.debug('Parsed data')
            prompt= f'Given the information from a report called {file_name}, use the template: {metadata}, fill al the required information according to the report and generate a json file using " for all the tags. Include much information as possible. The report is: {md}'
            instructions = f'Use the format and fill the required fields to generate a json file using double quotes. Use only the information given. If data not present, colocate as unknown. Return only the json format, no extra text. For date: yyyy-mm-dd. If mm or dd missing default June 1st. FYnn, nn is the year. Include no_bid in type according to the document tittle. Format to fill: {metadata}'
            response = llm._call_client(prompt,instructions)
            verify,data = file_manager.verify_json(response)
            if verify:
                db.collect_data(file_name,data,md)
                new_file_name = file_name + '.json'
                profile = rf'C:/Users/Cristopher Hdz/Desktop/Test/WordAnalizer/Files/json/{new_file_name}'
                with open(profile,'w',encoding='utf-8') as file:
                    file.write(response)
                logger.info(f'File written: {file_name}')
            else:
                missing.append(file_name)
                logger.debug(f'JSON response in wrong format for file: {file_name}')
        else:
            pass

print(f'Files converted.\nMissing files:\n{missing}\n')
#db.init()
db.update_db_records()