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
function enterDoor() {
    const transition = document.getElementById("transition");
    const door = document.querySelector(".door");
    document.getElementById("whiteboard-text").style.display = "block";

    const btn = document.querySelector(".door-btn");
    const roomImage = document.getElementById("room-image");

    btn.disabled = true;

    // Start fade overlay
    transition.classList.remove("fade-in");
    transition.classList.add("fade-out");

    door.classList.add("vanish");

    setTimeout(() => {
        // Swap content behind the door
        document.querySelector(".door-title").innerText = "ROOM 1";
        document.getElementById("display").innerText = "You entered the whiteboard room!";
        document.body.style.backgroundColor = "#c2b280";
        roomImage.style.display = "block";
        document.getElementById("whiteboard-svg").style.display = "block";


        // Fade overlay back in
        transition.classList.remove("fade-out");
        transition.classList.add("fade-in");

        // Re-enable button after fade-in
        setTimeout(() => btn.disabled = false, 600);
    }, 600);
}

function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function switchToClassroom() {
    const transition = document.getElementById("transition");
    const roomImage = document.getElementById("room-image");
    const classroomImage = document.getElementById("classroom-image");
    const whiteboardSvg = document.getElementById("whiteboard-svg");
    const whiteboardText = document.getElementById("whiteboard-text");
    const speechBubble = document.getElementById("speechBubble");
    // Start fade overlay
    transition.classList.remove("fade-in");
    transition.classList.add("fade-out");

    setTimeout(() => {
        // Swap to classroom
        document.querySelector(".door-title").innerText = "ROOM 2";
        document.getElementById("display").innerText = "You entered the classroom!";
        roomImage.style.display = "none";
        whiteboardSvg.style.display = "none";
        whiteboardText.style.display = "none";
        classroomImage.style.display = "block";
        speechBubble.style.display = "block";
    }, 600)

    // Fade overlay back in
    transition.classList.remove("fade-out");
    transition.classList.add("fade-in");

    // Show loading screen
    showLoadingScreen();
    await wait(3000); // show it for 3 seconds
    hideLoadingScreen();
}

let students = [];
class Student {
    constructor(eleid, name,top,left,width,imgpath) {
        this.eleid = eleid;
        this.name = name;
        this.img = null; // store the DOM element
        students.push(this);
        this.top = top 
        this.left = left 
        this.width = width 
        this.imgPath = imgpath
    }

    drawOnScreen() {
        if (this.img) this.img.remove();

        this.img = document.createElement("img");
        this.img.src = this.imgpath;
        this.img.id = this.eleid;
        this.img.style.position = "absolute";
        this.img.style.top = this.top;
        this.img.style.left = this.left;
        this.img.style.width = this.width;
        this.img.style.height = "auto";
        this.img.style.imageRendering = "pixelated";
        this.img.style.zIndex = 10;

        // Add it to the DOM
        document.body.appendChild(this.imgpath);
    }
}
// a 
let loadingInterval;

function showLoadingScreen() {
    const loadingScreen = document.getElementById("loading-screen");
    const loadingText = document.getElementById("loading-text");
    let dots = 1;

    loadingScreen.style.display = "flex";

    // Animate dots
    loadingInterval = setInterval(() => {
        dots = dots % 3 + 1; // cycle 1 → 2 → 3 → 1
        loadingText.textContent = "Loading" + ".".repeat(dots);
    }, 500);
}

function hideLoadingScreen() {
    const loadingScreen = document.getElementById("loading-screen");
    clearInterval(loadingInterval);
    loadingScreen.style.display = "none";
}

