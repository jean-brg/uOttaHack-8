# Flask
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
# File and data management
import time, json
# Threads
from concurrent.futures import ThreadPoolExecutor

# Consistent strategy for querying AIs
from ai_interface import AIModelDefinition, prompt_AI

# The models that will be queried for questioning (as students)
MODELS = [
    AIModelDefinition(name="xiaomi/mimo-v2-flash:free", temperature=0.8),
    AIModelDefinition(name="xiaomi/mimo-v2-flash:free", temperature=0.8),
    AIModelDefinition(name="xiaomi/mimo-v2-flash:free", temperature=0.8),
    AIModelDefinition(name="deepseek/deepseek-v3.2", temperature=0.2) # Costs $$$

    #"google/gemini-3-flash-preview",
    #"anthropic/claude-sonnet-4.5",
    #"openai/gpt-oss-120b", # Costs $$  ELIMINATED due to refusing instructions
    #"allenai/molmo-2-8b:free", # Eliminated due to refusing instructions
    #"google/gemini-2.0-flash-lite-001" # Costs $$
]

# APP INIT
app = Flask(__name__)
CORS(app)

# HOME ROUTE
@app.route("/")
def home():
    return render_template("index.html")

# GET list of models
@app.route('/api/get-models', methods=['GET'])
def get_models():
    # Return a list of all model names to the client
    return jsonify([model.getName() for model in MODELS])

# POST request for Direct AI agent prompt
@app.route('/api/prompt', methods=['POST'])
def execute_prompt():
    # Save the initial time and JSON arguments
    args = request.get_json()

    # Get the provided arguments
    prompt = args.get('prompt')
    modelname = args.get('model') or "xiaomi/mimo-v2-flash:free"
    constraints = args.get('constraints')

    return prompt_AI(prompt, constraints, modelname, temperature=0)

# Topic Management
topic = "Basic structure of an atom" # What topic the user is responsible for teaching
lesson_overview = [] # A list of "subtopics" that the user must cover in order to get a good score
completed_lesson = [] # Information the user has contributed to far to their lesson
questions = [] # A list of questions asked by each model, anonymized so the master AI isn't biased

def promptAllQuestions(prompt: str, constraints: str):
    # Save the initial time
    init_time = time.time()

    def query_model(model: AIModelDefinition):
        # Use the api_interface to prompt the specified AI. They have inheirant temperature values already.
        return model.prompt(message=prompt,constraints=constraints)

    # Use ThreadPoolExecutor to run all requests concurrently
    with ThreadPoolExecutor(max_workers=len(MODELS)) as executor:
        responseArray = list(executor.map(query_model, MODELS))

    return {
        "questions": [response["message"] for response in responseArray],
        "total_tokens": sum([response["tokens"] for response in responseArray]),
        "total_time": time.time() - init_time #time elapsed for all AI calls
    }

@app.route('/api/post-topic', methods=["POST"])
def postTopic():
    # Accepts the topic and generates a lesson overview
    global topic, lesson_overview
    args = request.get_json()
    topic = args.get('topic')

    lesson_overview = query_lesson_overview()

@app.route('/api/post-lesson', methods=["POST"])
def postLesson():
    global questions, lesson_overview, topic
    # Takes the user's input lesson data and returns AIs' questions
    # Save the JSON arguments
    args = request.get_json()
    lesson = args.get('lesson')

    # Clear the stored lesson data
    completed_lesson = []

    # Append the first piece of data to the lesson (the user's input)
    completed_lesson.append(lesson) 
    
    # print(lesson_overview)

    # Prompt all AI models concurrently for questions
    question_responses = promptAllQuestions(f'You are a middle school-level student learning about "${topic}"; The teacher\'s lesson is the following: "${lesson}".\nFind 3 questions to ask the teacher from basic to more challenging. It can be further clarification, extended knowledge or even rephrasing.', constraints="Reply with a list of objects with key 'question' (str) and 'difficulty' (int from 0-2 where 0 is easy). The list should be contained in a single key, 'questions'.")

    print(question_responses)

    # Extract the questions from the responses
    questions = question_responses['questions']

    sorted_questions = prompt_AI(
        prompt=f"Given the following list of questions, remove duplicate questions. Questions:\n{questions}",
        constraints="Answer in purely in JSON, no intro or anything with: an array of elements, each with the key 'question' and the value being each unique question. Don't add your own keys. If there are more than 6 uniques, pick the best 6"
    )

    parsed_questions = json.loads(sorted_questions["message"])

    print(parsed_questions)

    return jsonify(parsed_questions)   

@app.route('/api/get-questions', methods=["GET"])
def getQuestions():
    global questions
    return jsonify(questions)

@app.route('/api/post-answers', methods=["POST"])
def postAnswers():
    # Accepts an array of answers from the user, corresponding to the questions. The answers array must be equal in size to the questions array.
    global questions
    
    args = request.get_json()
    answers = args.get('answers')

    print(questions)

    for i in range(len(questions)):
        q = json.loads(questions[i])
        q['answer'] = answers[i]
        questions[i] = json.dumps(q)
    
    return jsonify(questions)

def query_lesson_overview():
    # Gemini, acting as an expert on the topic, will generate a lesson overview
    response = prompt_AI(
        prompt=('Generate a lesson overview in an array for this topic: "' + topic + '".'),
        constraints=('You are an expert on "' + topic + '" teaching at an intermediary level. If you choose to include any math, it should be in ASCII math format.'),
        model="google/gemini-2.0-flash-lite-001"
    )

    return response

# Run the app on localhost with flask
if __name__ == "__main__":
    app.run(debug=True)