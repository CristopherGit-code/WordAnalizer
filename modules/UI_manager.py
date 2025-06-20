from modules.config import Settings
from modules.db import DataBase
from modules.file_handler import File_handlder
from modules.llm_client import Client
import logging

logger = logging.getLogger(name=f'File.{__name__}.UI')

class UI:
    def __init__(self):
        self.merged_data = ''
        self.settings = Settings("wl_analysis.yaml")
        self.db = DataBase(self.settings)
        self.client = Client(self.settings)
        self.file_manager = File_handlder()

    def _get_db_response(
            self,
            name_list,
            year=2010,
            type=None,
            region=None,
            customer=None,
            product=None
        ):
        db_query = self.db.build_query(name_list,year,type,region,customer,product)
        db_response = self.db.sort_files(db_query)
        lists = [list(group) for group in zip(*db_response)]
        return lists
    
    def manage_filter(self,year,type,region,customer,product):
        self.client.reset_chat() # Reset to explain the mew filters
        # TODO: fix no_bid problem
        responses = self._get_db_response(['t.metadata.file_name','t.content'],year,type,region,customer,product)
        if not responses:
            self.merged_data = 'No data, retry'
            return ['No files found with that filter']
        else:
            self.merged_data = self.file_manager.merge_md(responses[1])
            return responses[0]
        
    def get_client_analysis(self,prompt,message_history,system_instructions=''):
        query = prompt + f' given the data in {self.merged_data}'
        logger.debug(query)
        return self.client.provide_analysis(query, system_instructions)

    def get_client_filter(self,prompt:str):
        r_dict = self.client.filter_files(prompt)
        year = r_dict[0]
        type = r_dict[1]
        region = r_dict[2]
        customer = r_dict[3]
        product = r_dict[4]
        lists = self.manage_filter(year,type,region,customer,product)
        message = f'Filter applied to prompt: {r_dict}'

        return lists,message
    
    def available_filters(self):
        responses = self._get_db_response(
            ['t.metadata.report_date','t.metadata.type','t.metadata.regions[0].region']
        )
        years = [int(date[:4]) for date in responses[0]]
        years.insert(0,2010)
        unique_years = sorted(set(years))

        responses[1].insert(0,"")
        unique_type = sorted(set(responses[1]))

        responses[2].insert(0,"")
        unique_region = sorted(set(responses[2]))

        return unique_years,unique_type,unique_region
    
    def manage_files(self,new_files):
        return 'Pass'