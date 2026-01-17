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
from typing import List, Optional

DOTENV_PATH = './.env'
OPENROUTER_API_KEY = dotenv.get_key(dotenv_path=DOTENV_PATH, key_to_get="OPENROUTER_API_KEY")
GEMINI_API_KEY = dotenv.get_key(dotenv_path=DOTENV_PATH, key_to_get="GEMINI_API_KEY")

MODELS = [
    "xiaomi/mimo-v2-flash:free",
    "xiaomi/mimo-v2-flash:free",
    "xiaomi/mimo-v2-flash:free",
    # "openai/gpt-5.2",
    # "deepseek/deepseek-v3.2",
    # "google/gemini-3-flash-preview",
    # "anthropic/claude-sonnet-4.5",
    "google/gemini-2.0-flash-lite-001",
    "meta-llama/llama-3.1-405b-instruct:free"
]

def prompt_AI(prompt:str, constraints, model="google/gemini-2.0-flash-lite-001", service="openrouter", temperature=0) -> dict:
    init_time = int(time.time()) # get the initial call time
    error_info = 'Something went wrong.'

    try:
        if(service == 'openrouter'):
            # Query the OpenRouter API using requests
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": "Bearer " + OPENROUTER_API_KEY
                },
                json={
                    "model": model,
                    "response_format": { "type": "json_object" },
                    "messages": [
                        { "role": "system", "content": constraints },
                        { "role": "user", "content": prompt }
                    ],
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
                    error_info = responsedict['error']['metadata']['raw']
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
    except FileExistsError: 
        return {
            'model': model,
            'start_time': init_time,
            'end_time': int(time.time()),
            'tokens': 0,
            'message': error_info,
            'status': 'fail'
        }
    
print(prompt_AI('Why is the sky blue?', 'Reply in one sentence or less. Name your response key "response".', model='google/gemini-2.0-flash-lite-001'))