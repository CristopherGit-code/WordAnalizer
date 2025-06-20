import oci,logging
from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference import models
from .config import Settings
import ast

logger = logging.getLogger(name=f'File.{__name__}----------->')

# General variables --------------------------
MAX_TOKENS = 600
TEMPERATURE = 1
FREQ_PENALTY = 0
TOP_P = 0.75
TOP_K = 0
PREAMBLE = 'Answer in maximum, 200 words'
MESSAGE = ''

class Client:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.config = oci.config.from_file(
            self.settings.oci_client.config_path, 
            self.settings.oci_client.configProfile)
        self.endpoint = self.settings.oci_client.endpoint
        self.client = GenerativeAiInferenceClient(
            config=self.config, 
            service_endpoint=self.endpoint, 
            retry_strategy=oci.retry.NoneRetryStrategy(), 
            timeout=(10,240))
        
        self.chat_detail = models.ChatDetails()
        self.chat_detail.serving_mode = models.OnDemandServingMode(
            model_id=self.settings.oci_client.model_id)
        self.chat_detail.compartment_id = self.settings.oci_client.compartiment

        self.message_db = {}
        self.message_history = [] # user

        self.chat_request = models.CohereChatRequest()
        self.chat_request.preamble_override = PREAMBLE # user
        self.chat_request.message = MESSAGE #user
        self.chat_request.max_tokens = MAX_TOKENS
        self.chat_request.temperature = TEMPERATURE
        self.chat_request.frequency_penalty = FREQ_PENALTY
        self.chat_request.top_p = TOP_P
        self.chat_request.top_k = TOP_K
        self.chat_request.chat_history = self.message_history #user    
        
    def get_chat_details(self):
        self.chat_detail.chat_request = self.get_chat_request()

        return self.chat_detail
    
    # Chat parameters
    def get_chat_request(self):
        return self.chat_request
    
    def set_chat_request(self, prompt, instructions):
        self.chat_request.preamble_override = PREAMBLE + instructions # user (keep 200 word limit)
        self.chat_request.message = prompt #user
    
    def _call_client(self,u_prompt, sys_instructions=''):
        self.message_history.append(models.CohereUserMessage(message=u_prompt))
        try:
            self.set_chat_request(u_prompt, sys_instructions)
            client_config = self.get_chat_details()
            chat_response = self.client.chat(client_config)
            generated_response = chat_response.data.chat_response.text
        except oci.exceptions.ServiceError as s:
            logger.debug(s)
            generated_response = f'Error in fetching the message: {s.message}'
        except Exception as e:
            logger.debug(e)
            generated_response = 'General internal error'
        self.message_history.append(models.CohereChatBotMessage(message=generated_response))

        return generated_response
    
    def provide_analysis(self, query:str, u_instructions:str) -> str:
        prompt = self.settings.analysis_prompt + query
        instructions = self.settings.analysis_instructions + u_instructions
        response = self._call_client(prompt,instructions)
        return response

    def filter_files(self, query:str) -> list:
        prompt = self.settings.filter_prompt + query
        instructions = self.settings.filter_instructions
        response = self._call_client(prompt, instructions)
        try:
            r_dict = ast.literal_eval(response)
        except Exception as e:
            r_dict = [2010,None,None,None]
        return r_dict

    # TODO: Set each user to particular history, missing
    def reset_chat(self):
        self.message_history = []

def main():
    llm = Client()
    ans = llm.botConversation('what is the capital of congo?')
    print(ans)
    

if __name__ == "__main__":
    main()