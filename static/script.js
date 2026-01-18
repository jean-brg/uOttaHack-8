async function getData() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/data');
        const data = await response.json(); //Convert JSON string to JS object
        console.log(data.message); // Outputs: "Connected to Python! "
        document.getElementById('display').innerText = data.message;
    } catch (error) {
        console.error('Error fetching data:', error);
    }
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

function switchToClassroom() {
    const transition = document.getElementById("transition");
    const roomImage = document.getElementById("room-image");
    const classroomImage = document.getElementById("classroom-image");
    const whiteboardSvg = document.getElementById("whiteboard-svg");
    const whiteboardText = document.getElementById("whiteboard-text");

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

        // Fade overlay back in
        transition.classList.remove("fade-out");
        transition.classList.add("fade-in");
    }, 600);
}
