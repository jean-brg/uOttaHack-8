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
    AIModelDefinition(name="deepseek/deepseek-v3.2", temperature=0.2), # Costs $$$
    AIModelDefinition(name="google/gemini-2.0-flash-lite-001",temperature=0.4),
    AIModelDefinition(name="google/gemini-2.0-flash-lite-001",temperature=0.4)

    #"google/gemini-3-flash-preview",
    #"anthropic/claude-sonnet-4.5",
    #"google/gemini-2.0-flash-lite-001" # Costs $$
]

# The model used for mission-critical calculations (rubric lesson plan, question moderation, objective completion)
MASTER_MODEL = "google/gemini-2.0-flash-lite-001"
master = AIModelDefinition(MASTER_MODEL, 0)

# How many questions (students) will be asked?
NUM_Q = 6

# APP INIT
app = Flask(__name__)
CORS(app)

# HOME ROUTE
@app.route("/")
def home():
    return render_template("index.html")

# GET list of models
@app.route("/score")
def score():
    return render_template("score.html")

@app.route('/api/get-models', methods=['GET'])
def get_models():
    # Return a list of all model names to the client
    return jsonify([model.getName() for model in MODELS])

# Topic Management
topic = "Basic structure of an atom" # What topic the user is responsible for teaching
lesson_overview = [] # A list of "subtopics" that the user must cover in order to get a good score
user_lesson = "" # Information the user has contributed to far to their lesson
questions = [] # A list of sorted questions (and maybe their answers).
original_questions = [] # A list of questions asked by each model

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
        "questions": [json.loads(response["message"]) for response in responseArray],
        "total_tokens": sum([response["tokens"] for response in responseArray]),
        "total_time": time.time() - init_time #time elapsed for all AI calls
    }

@app.route('/api/post-topic', methods=["POST"])
def postTopic():
    # Accepts the topic and generates a lesson overview
    global topic, lesson_overview
    args = request.get_json()
    topic = args.get('topic')

    print(topic)

    lesson_overview = query_lesson_overview()
    return jsonify(lesson_overview)

@app.route('/api/post-lesson', methods=["POST"])
def postLesson():
    global questions, original_questions, topic, user_lesson
    # Takes the user's input lesson data and returns AIs' questions
    # Save the JSON arguments
    args = request.get_json()
    lesson = args.get('lesson')

    # Clear the stored lesson data
    user_lesson = lesson
    
    # Prompt all AI models concurrently for questions
    question_responses = promptAllQuestions(f'You are a middle school-level student learning about "${topic}"; The teacher\'s lesson is the following: "${lesson}".\nFind 3 questions to ask the teacher from basic to more challenging. It can be further clarification, extended knowledge or even rephrasing.', constraints="Reply with a list of objects with key 'question' (str) and 'difficulty' (int from 0-2 where 0 is easy). The list should be contained in a single key, 'questions'.")

    # Extract the questions from the responses
    original_questions = question_responses['questions']

    sorted_questions = prompt_AI(
        prompt=f"Given the following list of questions, remove duplicate questions. Questions:\n{original_questions}",
        constraints=f"Answer in purely in JSON, no intro or anything with: an array of elements, each with the key 'question' and the value being each unique question. Don't add your own keys. If there are more than ${NUM_Q} uniques, pick the best ${NUM_Q}",
        model=MASTER_MODEL
    )

    parsed_questions = json.loads(sorted_questions["message"])

    # Saved the nicely parsed list of objects
    questions = parsed_questions
    return jsonify(parsed_questions)   

@app.route('/api/get-questions', methods=["GET"])
def getQuestions():
    global questions
    return jsonify(questions)

@app.route('/api/post-answers', methods=["POST"])
def postAnswers():
    # Accepts an array of answers from the user, corresponding to the questions. The answers array must be equal in size to the questions array.
    global questions, user_lesson
    
    args = request.get_json()
    answers = args.get('answers')

    # Abort if the answers array is the wrong length
    if(not len(answers) == len(questions)): return None

    # Assign an answer to each question
    for i in range(len(answers)):
        questions[i]['answer'] = answers[i]

    # Return the player's final score
    return jsonify(query_lesson_score())

def query_lesson_overview():
    # Gemini, acting as an expert on the topic, will generate a lesson overview
    response = prompt_AI(
        prompt=('Generate a lesson overview in an array for this topic: "' + topic + '".'),
        constraints=('You are an expert on "' + topic + '" teaching at an intermediary level. If you choose to include any math, it should be in ASCII math format.'),
        model=MASTER_MODEL
    )

    return response

def query_lesson_score():
    # Analyze and compare the lesson score
    lessonstring = user_lesson
    questionsstring = json.dumps(questions)

    score = master.prompt(
        message=(f'Grade the following performance. The user was tasked with teaching the following topic: "${topic}". They initially provided the following lesson: "${lessonstring}". Afterwards, they were asked the following questions and gave the corresponding answers: ${questionsstring}. Provide a grade and feedback, considering lesson/answer accuracy, detail and relevancy. The grade is made up of 50% lesson and 50% questions. Be fair, grade should reflect performance.'),
        constraints=("Reply in JSON with three fields, 'percentage_grade' float between 0 and 1, 'letter_grade' (one of 'A+' (0.9 to 1), 'A' (0.85 to 0.9),'B' (0.7 to 0.85), 'C' (0.6 to 0.7), 'D' (0.5 to 0.6), or 'F' (0 to 0.5)) and 'feedback', an array of 4 strings containing bullet-point feedback.  Do not add additional fields. The top level should be an object, not an array. Be direct in your feedback and make it relevant to the grade.")
    )

    scoreout = json.loads(score['message'])
    return scoreout

# Run the app on localhost with flask
if __name__ == "__main__":
    app.run(debug=True)