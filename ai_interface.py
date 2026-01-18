'''
API Interface
Interfaces with OpenRouter and the Gemini API to provide prompt responses
'''
# File and data management
import os
import dotenv
import requests, json
import time
# AI agent
from google import genai
from pydantic import BaseModel, Field
from typing import List

DOTENV_PATH = './.env'
OPENROUTER_API_KEY = dotenv.get_key(dotenv_path=DOTENV_PATH, key_to_get="OPENROUTER_API_KEY")
GEMINI_API_KEY = dotenv.get_key(dotenv_path=DOTENV_PATH, key_to_get="GEMINI_API_KEY")

# The JSON format for a lesson plan
class LessonPlan(BaseModel):
    # The lesson plan name
    subtopics: List[str] = Field(description="The lesson's subtopics, e.g. what needs to be taught for the topic to be understood")

class AIModelDefinition:
    def __init__(self, name: str, temperature: int):
        self.name = name
        self.temperature = temperature

    def __repr__(self):
        return '<AIModelDefinition: ' + (self.name) + ' @ ' + (self.temperature) + '>'
    
    def getName(self):
        return self.name
    
    def prompt(self, message:str, constraints=None):
        '''Prompts the AI model using its inherant temperature value'''
        return prompt_AI(prompt=message, constraints=constraints, model=self.name, service="openrouter", temperature=self.temperature)
    
# Gemini client for gemini api calls
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

def prompt_AI(prompt:str, constraints=None, model="google/gemini-2.0-flash-lite-001", service="openrouter", temperature=0) -> dict:
    '''
    Prompt any AI using openrouter or the Gemini API (coming soon). 
    The result will be returned as a JSON-compatiable dict. 
    '''
    init_time = int(time.time()) # get the initial call time
    error_info = 'Something went wrong.'

    try:
        if(service == 'openrouter'):
            messages = [
                { "role": "user", "content": prompt },
                { "role": "assistant", "content": '{' } # Encourage the AI to follow JSON syntax
            ]

            # Only include constraints if they are defined
            if(not constraints is None):
                messages.insert(0, { "role": "system", "content": constraints })

            print(messages)

            # Query the OpenRouter API using requests
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": "Bearer " + OPENROUTER_API_KEY
                },
                json={
                    "model": model,
                    "response_format": { "type": "json_object" },
                    "messages": messages,
                    "temperature": temperature,
                    "provider": {
                        'require_parameters': True
                    }
                }
            )

            # Get the model API's response as a dictionary
            responsedict = response.json()
            
            if(not 'choices' in responsedict.keys()):
                # If there aren't any responses, it's a fail
                if('error' in responsedict): 
                    error_info = str(responsedict['error'])
                raise Exception(responsedict)

            # Show the responses array (we only evaluate the first one though)
            choices = responsedict['choices']

            # Get the success and message from the API response
            success = ((len(choices) > 0) and ('message' in choices[0].keys()) and ('content' in choices[0]['message'].keys()))
            if(not success): raise Exception('Missing properties in the expected result')
            
            # Get the resulting message
            message = choices[0]['message']['content']
            
            # Return the useful information
            result = {
                # Report the model again, just cause
                "model": model,

                # Metrics
                "start_time": init_time,
                "end_time": int(time.time()),
                "tokens": responsedict['usage']['total_tokens'],

                # Prompt response
                'message': message,
                'status': 'success'
            }

            return result
        elif(service == 'gemini'):
            raise Exception('Gemini service is not supported at this time')
        else:
            raise Exception('Invalid service')
    except BaseException: 
        return {
            'model': model,
            'start_time': init_time,
            'end_time': int(time.time()),
            'tokens': 0,
            'message': error_info,
            'status': 'fail'
        }

if __name__ == '__main__':
    print(prompt_AI('Why is the sky blue?', 'Reply in one sentence or less. Name your response key "response".', model='google/gemini-2.0-flash-lite-001'))