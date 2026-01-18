let questions = [
    /*{ // A single questioner object. These are grouped according to the LLM that asked them and remain in that order.
        "questions": [ 
            {
                question: "Why?", // The question to be asked to the user, as a string
                difficulty: 0, // 0 is easy, 3 is hard
            }
        ]
    }*/
];
let topic = ""; // Keep track of the topic for display purposes

async function promptRequest(prompt, model='xiaomi/mimo-v2-flash:free', constraints='Use only one sentence to respond.') {
    // Prompt an AI model with a request using the Python backend
    return await fetch(
        'http://127.0.0.1:5000/api/prompt',
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                prompt,
                model,
                constraints
            })
        }
    ).then(resp => resp.json());
}

async function promptAllModels(prompt, constraints='Use only one sentence to respond.') {
    return await fetch(
        'http://127.0.0.1:5000/api/prompt-all',
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                prompt,
                constraints
            })
        }
    ).then(resp => resp.json())
}

async function submitLesson() {
    // This function submits a lesson, waits for a response and then afterwards returns the questions asked by each LLM.

    // Get all user-submitted data
    let lesson_topic = document.querySelector("#lesson_topic").value.trim()
    let lesson_content = document.querySelector("#lesson_content").value.trim()
    let loading_icon = document.querySelector("#loading")

    // Save the topic in global variable
    topic = lesson_topic;

    // Show the loading gif
    loading_icon.style.display = "block"

    // If the lesson topic is missing
    if (lesson_topic == "" || lesson_content == "") {
        alert("Missing lesson input value");
        return undefined;
    }

    // Make a POST request. Submits the lesson topic and user lesson overview to the backend, which will reply with AI-generated questions
    let allQuestions = fetch(
        'http://127.0.0.1:5000/api/post-lesson',
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                lesson: lesson_content
            })
        }
    ).then(resp => resp.json())

    // Wait for the promise to resolve
    let data = await allQuestions;

    // Hide the loading indicators
    loading_icon.style.display = "none"

    // Each element will be sent to the student's speech 
    document.querySelector("#questions").innerText = data.map(q => q.question).join("\n\n")

    // Store the questions in a global variable
    questions = data;
    
    return questions;
}