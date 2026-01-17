const models = [
    "xiaomi/mimo-v2-flash:free",
    //"openai/gpt-5.2",
    //"deepseek/deepseek-v3.2",
    //"google/gemini-3-flash-preview",
    //"anthropic/claude-sonnet-4.5",
    "openai/gpt-oss-120b:free",
    "meta-llama/llama-3.1-405b-instruct:free"
];

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

        promptRequest('2+2', models[1]).then(data => {
            console.log(data);
            document.getElementById('display').innerText = data.message;
        })
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}