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
    transition.classList.add("fade-out");

    door.classList.add("vanish");

    setTimeout(() => {
        // Swap content behind the door
        document.querySelector(".door-title").innerText = "ROOM 2";
        document.getElementById("display").innerText = "You entered a new room!";
        document.body.style.backgroundColor = "#2a2a2a";
        roomImage.style.display = "block";


        // Fade overlay back in
        transition.classList.remove("fade-out");
        transition.classList.add("fade-in");

        // Re-enable button after fade-in
        setTimeout(() => btn.disabled = false, 600);
    }, 600);
}
