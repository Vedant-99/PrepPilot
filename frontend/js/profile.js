// Grab the elements we need
const form = document.getElementById("profile-form");
const roleSelect = document.getElementById("target-role");
const yearSelect = document.getElementById("study-year");
const skillsList = document.getElementById("skills-list");
const customInput = document.getElementById("custom-skill");
const addSkillBtn = document.getElementById("add-skill-btn");
const message = document.getElementById("form-message");
const saveBtn = form.querySelector(".save-btn");


// Shows a message under the form (green when isSuccess is true)
function showMessage(text,isSuccess) {
    message.textContent = text;
    message.classList.toggle("success", isSuccess);
}

// To get the initials of name
function getInitials(fullName) {
    const words = fullName.trim().split(/\s+/);
    return words.slice(0,2).map((word) => word[0]).join("").toUpperCase(); 
}

//  to return every skill checkbox ->  present ones and the ones user added
function getSkillBoxes() {
    return skillsList.querySelectorAll('input[name="skills"]');
}

// find the checkbox of a skill by name, ignoring upper/lower case
function findSkillBox(name) {
    for (const box of getSkillBoxes()) {
        if(box.value.toLowerCase()===name.toLowerCase()) {
            return box;
        }
    }
    return null;
}


// Skills: add a new chip, or tick if it is already exists
function addSkill(name) {
    const existing = findSkillBox(name);
    if(existing) {
        existing.checked = true;
        return;
    }
    // Build: 
    const label = document.createElement("label");
    label.className = "chip";

    const box  = document.createElement("input");
    box.type = "checkbox";
    box.name = "skills";
    box.value = name;
    box.checked = true;

    const text = document.createElement("span");
    text.textContent = name;    

    label.append(box,text);
    skillsList.append(label);
}

// What happens when the user clicks And (or press enter in the box)
function handleAddSkills() {
    const name = customInput.value.trim();
    if(name==""){
        showMessage("Type a skill name first.", false);
        return;
    }
    if(name.length > 30){
        showMessage("A skill name can have at most 30 letters.", false);
        return;
    }
    addSkill(name);
    customInput.value ="";
    customInput.focus();
    showMessage("", false);
}
addSkillBtn.addEventListener("click",handleAddSkills);

// Enter in the skill box must add the skill, not submit the whole form
customInput.addEventListener("keydown", (event) =>{
    if(event.key === "Enter"){
        event.preventDefault();
        handleAddSkills();
    }
});


//  Load: who is logged in, and what did they save before?
async function loadPage(){
    try {
        //  1) The logged-in user-> for sidebar
        const meResponse = await fetch("/api/auth/me");
        if(meResponse.status === 401) {
            window.location.href = "login.html";
            return;
        }
        const user = await meResponse.json();
        document.getElementById("user-name").textContent = user.full_name;
        document.getElementById("user-email").textContent = user.email;
        document.getElementById("user-initials").textContent = getInitials(user.full_name);

        // 2) the saved profile (null if the user never saved one)
        const profileResponse = await fetch("/api/profile");
        const data = await profileResponse.json();
        if(data.profile) {
            fillForm(data.profile);
        }
    } catch(error) {
        showMessage("Cannot reach the server. Is it running?",false);
    }
}


//  Put the saved values back into the form
function fillForm(profile) {
    roleSelect.value = profile.target_role;
    yearSelect.value = String(profile.study_year);
    for(const skill of profile.skills) addSkill(skill);
}



// Save 
form.addEventListener("submit", async(event) => {
    event.preventDefault(); // stops page from relaoding

    // check the dropdowns before we send anything
    if(roleSelect.value===""){
        showMessage("Please choose your target role.", false);
        return;
    }
    if(yearSelect.value===""){
         showMessage("Please choose your year of study.",false);
         return;
    }

    // Collect the ticked skills into the list
    const skills = [];
    for(const box of getSkillBoxes()){
        if(box.checked) {
            skills.push(box.value);
        }
    }
    saveBtn.disabled = true;
    showMessage("Saving...",true);

    try {
        const response = await fetch("/api/profile", {
            method: "PUT",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({
                target_role: roleSelect.value,
                study_year: Number(yearSelect.value),
                skills: skills,
            }),
        });
        if(response.status === 401){
            window.location.href = "login.html";
            return;
        }
        if(!response.ok) {
            showMessage("Could not save. Please check your answers.",false);
            return;
        }
        showMessage("Profile saved!",true);
    } catch(error) {
        showMessage("Cannot reach the server. Is it running?",false);
    } finally {
        saveBtn.disabled= false;
    }
});

// Log out button
document.getElementById("logout-btn").addEventListener("click", async() => {
    await fetch("/api/auth/logout", {method: "POST"});
    window.location.href = "login.html";
});

// Runs when the page opens
loadPage();