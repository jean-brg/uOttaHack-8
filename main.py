# IMPORTS
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import dotenv
import requests, json
import time

API_KEY = dotenv.get_key(dotenv_path="./.env", key_to_get="BEN_OPENROUTER")

# APP INIT
app = Flask(__name__)
CORS(app)

# HOME ROUTE
@app.route("/")
def home():
    return render_template("index.html")

# SAMPLE DATA ROUTE
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
            "Authorization": "Bearer " + API_KEY
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

# RUNNER
if __name__ == "__main__":
    app.run(debug=True)