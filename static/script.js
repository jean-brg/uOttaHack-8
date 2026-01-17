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

async function getData() {
    // Stuff to do when button!
    try {
        promptRequest('What is the meaning of life?').then(data => {
            console.log(data);
            document.getElementById('display').innerText = data.message;
        })

        promptRequest('Why is the sky blue?').then(data => {
            console.log(data);
            document.getElementById('display').innerText = data.message;
        })

        promptRequest('2+2').then(data => {
            console.log(data);
            document.getElementById('display').innerText = data.message;
        })
    } catch (error) {
        console.error('Error fetching data:', error);
    }
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
    // Get all objects
    lesson_topic = document.querySelector("#lesson_topic").value.trim()
    lesson_content = document.querySelector("#lesson_content").value.trim()
    loading_icon = document.querySelector("#loading")

    loading_icon.style.display = "block"

    if (lesson_topic == "" || lesson_content == "") {
        alert("Missing lesson input value");
        return undefined
    }

    allQuestions = promptAllModels(`You are a student learning about "${lesson_topic}"; The teacher's lesson is "${lesson_content}". Find 5 questions to ask the teacher from easy to more challenging to push the teacher with their teaching skills.`, constraints="Only reply with questions, one sentence is length")

    console.log(allQuestions)

    allQuestions.then((data) => {
        loading_icon.style.display = "none"
        document.querySelector("#questions").innerText = data["questions"].join("\n\n");
        return data
    })
}