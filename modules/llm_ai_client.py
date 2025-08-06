from modules.util.openai_api import LLM_Open_Client
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel
from typing import Literal
import logging
from typing import List
import re

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=f"OPENAI_CLIENT.{__name__}")

class Query_Fields(BaseModel):
    year: str = "All"
    type: Literal['win','loss','no_bid'] = ''
    region: str = ''
    customer: str = ''
    product: str = ''

class Search_Query(BaseModel):
    search_dict: List[Query_Fields]

class SearchAgent:
    """ Search agent in charge of generating the dictionary for the DB """

    _instance = None
    _initialized = False

    FORMAT_INSTRUCTION = (
        'Fill the list accoding to the required fields based explicity on the user query.\n'
        'DO NOT make up information, if the user does not provide information about one of the fields, set it to None.\n'
        'For year use the format yyyy. If the year is not specified, set the field to "All".\n'
        "For type if not specified, set the field to empty.\n"
        'For region use two letter abreviation for the requested country, infer the country from city or state. If not data from region, leave the field empty.\n'
        'For customer, fill the field with the provided customer, if not specified, set the field to empty.\n'
        'For product, fill the field with the provided product, only one, if not specified, set the field to empty.'
    )

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SearchAgent,cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.oci_client = LLM_Open_Client()
            self.model = self.oci_client.build_llm_client()
            self.create_agent()
            SearchAgent._initialized = True
    SYSTEM_INSTRUCTION = (
        "You are an agent in charge of converting a user natural language prompt into a list with specific fields.\n"
        "Year, type, region, customer, product should be selected according to the user query.\n"
        "DO NOT make up any information, if one of the fields is not provided, set it as None.\n"
        "Always return a python list."
    )
        
    def create_agent(self):
        self.tools = []
        self.search_agent = create_react_agent(
            model=self.model,
            tools=self.tools,
            prompt=self.SYSTEM_INSTRUCTION,
            response_format=(self.FORMAT_INSTRUCTION,Search_Query)
        )

    def build_dictionary(self,query):
        response = self.search_agent.invoke({"messages": [{"role": "user", "content": query}]})
        ans = response['structured_response'].search_dict[-1]
        s = str(ans)
        values = re.findall(r"(?:\w+)=('.*?'|\S+)", s)
        values = [v.strip("'") for v in values]
        logger.debug(values)
        return values

async def main_loop():
    agent = SearchAgent()
    query = "Give me loss documents in California"
    response = agent.build_dictionary(query)
    print("======== model response:")
    print(response)
    print(type(response))
    return

if __name__ == '__main__':
    import asyncio
    asyncio.run(main_loop())