# Flask
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
# File and data management
import os
import dotenv
import requests, json
import time
# Threads
import threading
# AI agent
# from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional

class LessonPlan(BaseModel):
    # The lesson plan name
    subtopics: List[str] = Field(description="The lesson's subtopics, e.g. what needs to be taught for the topic to be understood")

DOTENV_PATH = './.env'
OPENROUTER_API_KEY = dotenv.get_key(dotenv_path=DOTENV_PATH, key_to_get="OPENROUTER_API_KEY")
# GEMINI_API_KEY = dotenv.get_key(dotenv_path=DOTENV_PATH, key_to_get="GEMINI_API_KEY")

MODELS = [
    "xiaomi/mimo-v2-flash:free",
    "xiaomi/mimo-v2-flash:free",
    "xiaomi/mimo-v2-flash:free",
    # "openai/gpt-5.2",
    # "deepseek/deepseek-v3.2",
    # "google/gemini-3-flash-preview",
    # "anthropic/claude-sonnet-4.5",
    "openai/gpt-oss-120b:free",
    "allenai/molmo-2-8b:free"
]

# Gemini client will be used for overall research and management
# gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# APP INIT
app = Flask(__name__)
CORS(app)

# HOME ROUTE
@app.route("/")
def home():
    return render_template("index.html")

# POST request for Direct AI agent prompt
@app.route('/api/prompt', methods=['POST'])
def execute_prompt():
    # Save the initial time and JSON arguments
    init_time = time.time()
    args = request.get_json()

    # Get the provided arguments
    prompt = args.get('prompt')
    model = args.get('model') or "xiaomi/mimo-v2-flash:free"
    constraints = args.get('constraints')

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + OPENROUTER_API_KEY
        },
        data=json.dumps({
            "model": model,
            "messages": [
                { "role": "system", "content": constraints },
                { "role": "user", "content": prompt }
            ],
            "temperature": 0
        })
    )

    # Get the model API's response as a dictionary
    responsedict = response.json()
    if(not 'choices' in responsedict.keys()):
        # If there aren't any responses, it's a fail
        return jsonify({
            "start_time": init_time,
            "end_time": (time.time()),
            "tokens": 0,
            "message": responsedict['error']['message'] if ('error' in responsedict.keys()) else 'Something went wrong',
            "success": False
        })

    # Show the responses array (we only evaluate the first one though)
    choices = responsedict['choices']

    # Get the success and message from the API response
    try:
        success = ((len(choices) > 0) and ('message' in choices[0].keys()) and ('content' in choices[0]['message'].keys()))
        if(not success): raise Exception()      # Shortcut to the failiure method if any properties are mising
        text = choices[0]['message']['content']
    except Exception:
        success = False
        text = 'Something went wrong.'
    
    # Return some useful information
    result = {
        # Report the model again, just cause
        "model": model,

        # Metrics
        "start_time": init_time,
        "end_time": (time.time()),
        "tokens": responsedict['usage']['total_tokens'],

        # Prompt response
        "message": text,
        "success": success
    }

    return jsonify(result)

# Topic Management
topic = "Basic structure of an atom" # What topic the user is responsible for teaching
lesson_overview = [] # A list of "subtopics" that the user must cover in order to get a good score
questions = [] # A list of questions asked by each model, anonymized so Gemini isn't biased

# Gemini Methods
def query_lesson_overview():
    # Gemini, acting as an expert on the topic, will generate a lesson overview
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        config=genai.types.GenerateContentConfig(
            system_instruction='You are an expert on "' + topic + '" teaching at an intermediary level. If you choose to include any math, it should be in KaTeX format, surrounded by $.',
            temperature=0,
            response_json_schema=LessonPlan.model_json_schema(),
            response_mime_type="application/json"
        ),
        contents='Generate a short lesson overview in an array for the topic "' + topic + '".' 
    )

    lo = LessonPlan.model_validate_json(response.text)
    return lo.subtopics

@app.route('/api/prompt-all', methods=['POST'])
def promptAll():
    init_time = time.time()
    args = request.get_json()

    prompt = args.get('prompt')
    constraints = args.get('constraints')

    responseArray = []

    for model in MODELS:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer " + OPENROUTER_API_KEY
            },
            data=json.dumps({
                "model": model,
                "messages": [
                    { "role": "system", "content": constraints },
                    { "role": "user", "content": prompt }
                ],
                "temperature": 0.2
            })
        )
        
        # Parse the response JSON
        responsedict = response.json()
        
        # Extract relevant data similar to execute_prompt()
        if 'choices' in responsedict and len(responsedict['choices']) > 0 and 'message' in responsedict['choices'][0]:
            text = responsedict['choices'][0]['message'].get('content', 'No content')
            success = True
            tokens = responsedict.get('usage', {}).get('total_tokens', 0)
        else:
            success = False
            text = responsedict.get('error', {}).get('message', 'Something went wrong')
            tokens = 0
        
        # Append the processed data
        responseArray.append({
            "message": text,
            "tokens": tokens
        })

    return jsonify({
        "questions": [response["message"] for response in responseArray],
        "total_tokens": sum([response["tokens"] for response in responseArray]),
        "total_time": time.time() - init_time
    })

# RUNNER
if __name__ == "__main__":
    app.run(debug=True)