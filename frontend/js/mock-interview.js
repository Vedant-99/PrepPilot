//  Find the parts of the page by their id
const messageLine = document.getElementById("mock-message");

const setupCard = document.getElementById("setup-card");
const questionCard = document.getElementById("question-card");
const finishCard = document.getElementById("finish-card");

const categorySelect = document.getElementById("category-select");
const difficultySelect = document.getElementById("difficulty-select");
const startBtn = document.getElementById("start-btn");

const progressDots = document.getElementById("progress-dots");
const progressText = document.getElementById("progress-text");
const qCategory = document.getElementById("q-category");
const qTopic = document.getElementById("q-topic");
const qDifficulty = document.getElementById("q-difficulty");
const questionText = document.getElementById("question-text");
const listenBtn = document.getElementById("listen-btn");

const answerBox = document.getElementById("answer-box");
const micBtn = document.getElementById("mic-btn");
const voiceStatus = document.getElementById("voice-status");

const keyPointsBox = document.getElementById("key-points-box");
const keyPointsText = document.getElementById("key-points-text");
const showPointsBtn = document.getElementById("show-points-btn");
const nextBtn = document.getElementById("next-btn");

const finishText = document.getElementById("finish-text");

// A line under the key points: "You covered 2 of 4 points" (made here, not in the HTML)
const keyPointsResult = document.createElement("p");
keyPointsResult.className = "points-result";
keyPointsBox.appendChild(keyPointsResult);

const restartBtn = document.getElementById("restart-btn");

//  Things we remember while page opens
const QUESTIONS_PER_ROUND =5;       // how many questions in one round
let questions = [];                 // the questions of this round
let currentIndex = 0;               // which questions of this round
let recognition = null;             // the speech-to-text helper
let isListening = false;            //true while mic is on

// Small helpers
function showMessage(text) {
    if(!text) {
        messageLine.hidden = true;
        return;
    }
    messageLine.textContent = text;
    messageLine.hidden = false;
}

// show only one of the three parts: setup, question or finish
function showOnly(card) {
    setupCard.hidden = true;
    questionCard.hidden = true;
    finishCard.hidden = true;
    card.hidden = false;
}

//  stop the voice --> read aloud and listening so nothing keeps running
function stopVoice() {
    if("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
    }
    if( recognition && isListening){
        recognition.stop();
    }
}

//  check login first
async function checkLogin(){
    try {
        const response = await fetch("/api/auth/me");
        //  401 -> not logged in, so go to login page
        if(response.status===401) window.location.href = "login.html";
    } catch(error) {
        showMessage("Cannot reach the server, Is it running?");
    }
}

//  Start the round
async function startInterview() {
    showMessage("");

    // Build  the address, like /api/questions?category=hr&difficulty=easy
    const params = new URLSearchParams();
    if(categorySelect.value) params.append("category", categorySelect.value);
    if(difficultySelect.value) params.append("difficulty", difficultySelect.value);
    
    try {
        const response = await fetch("/api/questions?"+ params.toString());

        if( response.status === 401){
            window.location.href = "login.html";
            return;
        }
        if(!response.ok){
            showMessage("Could not load questions. Try again.");
            return;
        }
        const data = await response.json();
        if(data.questions.length===0) {
            showMessage("No questions found for this choice. Try different filters.");
            return;
        }
        // Mix order, then keep only the first few questions
        questions = data.questions.sort(() => Math.random() -0.5).slice(0, QUESTIONS_PER_ROUND);
        currentIndex =0;

        showOnly(questionCard);
        showQuestion();
    } catch (error) {
        showMessage("Cannot reach the server, Is it running?");
    }
}

// ---------- Show the current question ----------
function showQuestion() {
    stopVoice();

    const q = questions[currentIndex];

    // textContent is safe: it shows text only and never runs HTML
    qCategory.textContent = q.category;
    qTopic.textContent = q.topic;
    qDifficulty.textContent = q.difficulty;
    questionText.textContent = q.question;

    // Clear the old answer and hide the old key points
    answerBox.value = "";
    keyPointsBox.hidden = true;
    keyPointsText.textContent = "";
    keyPointsResult.textContent = "";
    showPointsBtn.disabled = false;
    voiceStatus.textContent = "Mic is off. You can also type.";

    // Last question -> the button says Finish
    nextBtn.textContent = (currentIndex === questions.length - 1) ? "Finish round" : "Next question";

    progressText.textContent = `Question ${currentIndex + 1} of ${questions.length}`;
    drawDots();
}

// One dot for each question: finished ones and the current one are colored
function drawDots() {
    progressDots.innerHTML = "";
    for (let i = 0; i < questions.length; i++) {
        const dot = document.createElement("span");
        dot.className = "p-dot";
        if (i < currentIndex) dot.classList.add("done");
        if (i === currentIndex) dot.classList.add("current");
        progressDots.appendChild(dot);
    }
}

// Count the ticked boxes and show "You covered X of Y points"
function updateResult() {
    const allBoxes = keyPointsText.querySelectorAll("input[type=checkbox]");
    const tickedBoxes = keyPointsText.querySelectorAll("input[type=checkbox]:checked");
    keyPointsResult.textContent = `You covered ${tickedBoxes.length} of ${allBoxes.length} points. This is your own check, not an AI score.`;
}

// ---------- Key points (asked from the server only when clicked) ----------
async function showKeyPoints() {
    const q = questions[currentIndex];
    try {
        const response = await fetch(`/api/questions/${q.id}/key-points`);
        if (!response.ok) {
            showMessage("Could not load the key points.");
            return;
        }
        const data = await response.json();
        // key_points is one long text, and ";" separates the points
        const points = data.key_points.split(";").map((p) => p.trim()).filter((p) => p !== "");

        // Remove old boxes, then make one tick box for each point
        keyPointsText.innerHTML = "";
        points.forEach((point) => {
            const label = document.createElement("label");
            label.className = "point-item";

            const box = document.createElement("input");
            box.type = "checkbox";
            box.addEventListener("change", updateResult);   // count again on every tick

            const words = document.createElement("span");
            words.textContent = point;   // textContent is safe: text only

            label.appendChild(box);
            label.appendChild(words);
            keyPointsText.appendChild(label);
        });
        updateResult();   // shows "0 of X" at the start
        keyPointsBox.hidden = false;
        showPointsBtn.disabled = true;
    } catch (error) {
        showMessage("Cannot reach the server. Is it running?");
    }
}


// ---------- Next question or finish ----------
function goNext() {
    currentIndex++;
    if (currentIndex >= questions.length) {
        finishRound();
    } else {
        showQuestion();
    }
}

function finishRound() {
    stopVoice();
    finishText.textContent = `You practiced ${questions.length} questions. Run another round with a different category to keep improving.`;
    showOnly(finishCard);
}


// ---------- Voice: hear the question ----------
function hearQuestion() {
    if (!("speechSynthesis" in window)) {
        showMessage("Your browser cannot read aloud. Try Chrome or Edge.");
        return;
    }
    window.speechSynthesis.cancel();   // stop anything already speaking
    const speech = new SpeechSynthesisUtterance(questions[currentIndex].question);
    speech.lang = "en-IN";
    window.speechSynthesis.speak(speech);
}


// ---------- Voice: speak your answer ----------
function setupMic() {
    // Chrome and Edge use the name webkitSpeechRecognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    // Browser has no speech-to-text -> turn the mic button off
    if (!SpeechRecognition) {
        micBtn.disabled = true;
        voiceStatus.textContent = "Mic needs Chrome or Edge. You can type your answer.";
        return;
    }

    recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.continuous = true;   // keep listening until you stop it

    recognition.onstart = () => {
        isListening = true;
        micBtn.textContent = "Stop speaking";
        micBtn.classList.add("listening");
        voiceStatus.textContent = "Listening...";
    };

    // Add the finished words to the end of the answer box
    recognition.onresult = (event) => {
        for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
                const words = event.results[i][0].transcript.trim();
                answerBox.value = answerBox.value ? answerBox.value + " " + words : words;
            }
        }
    };

    recognition.onerror = (event) => {
        if (event.error === "not-allowed") {
            voiceStatus.textContent = "Mic is blocked. Allow the microphone, or type your answer.";
        } else {
            voiceStatus.textContent = "Mic problem. You can type your answer.";
        }
    };

    recognition.onend = () => {
        isListening = false;
        micBtn.textContent = "Start speaking";
        micBtn.classList.remove("listening");
        if (voiceStatus.textContent === "Listening...") {
            voiceStatus.textContent = "Mic is off. You can also type.";
        }
    };
}

function toggleMic() {
    if (!recognition) return;
    if (isListening) {
        recognition.stop();
    } else {
        recognition.start();
    }
}


// ---------- Button clicks ----------
startBtn.addEventListener("click", startInterview);
showPointsBtn.addEventListener("click", showKeyPoints);
nextBtn.addEventListener("click", goNext);
listenBtn.addEventListener("click", hearQuestion);
micBtn.addEventListener("click", toggleMic);
restartBtn.addEventListener("click", () => {
    showMessage("");
    showOnly(setupCard);
});

// ---------- Run when the page opens ----------
checkLogin();
setupMic();