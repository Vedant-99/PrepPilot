//  Find  the parts of the page (by their ids)
const form = document.getElementById("app-form");
const formTitle = document.getElementById("form-title");
const companyInput = document.getElementById("company");
const roleInput = document.getElementById("role");
const statusSelect = document.getElementById("status");
const dateInput = document.getElementById("applied-date");
const notesInput = document.getElementById("notes");
const message = document.getElementById("app-message");
const saveBtn = document.getElementById("save-app-btn");
const cancelBtn = document.getElementById("cancel-edit-btn");

// The 5 stages, in the same order as the columns on the page
const STAGES = ["wishlist", "applied", "interview", "offer", "rejected"];

// ---------- Things we remember while the page is open ----------
let applications = [];    // all applications of this user
let editingId = null;     // id of the application being edited (null = adding a new one)


// ---------- Small helpers ----------

// Show a message under the form (green when isSuccess is true)
function showMessage(text, isSuccess) {
    message.textContent = text;
    message.classList.toggle("success", isSuccess);
}

// First letter of the first 2 words, for the avatar circle
function getInitials(fullName) {
    const words = fullName.trim().split(/\s+/);
    return words.slice(0, 2).map((word) => word[0]).join("").toUpperCase();
}

// "2026-11-05" -> "5 Nov 2026"
function formatDate(text) {
    const date = new Date(text + "T00:00:00");
    return date.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
}


// ---------- Who is logged in? (for the top bar) ----------
async function loadUser() {
    try {
        const response = await fetch("/api/auth/me");
        // 401 -> not logged in, so go to the login page
        if (response.status === 401) {
            window.location.href = "login.html";
            return;
        }
        const user = await response.json();
        document.getElementById("user-name").textContent = user.full_name;
        document.getElementById("user-email").textContent = user.email;
        document.getElementById("user-initials").textContent = getInitials(user.full_name);
    } catch (error) {
        showMessage("Cannot reach the server. Is it running?", false);
    }
}


// ---------- Get all applications from the server ----------
async function loadApplications() {
    try {
        const response = await fetch("/api/applications");
        if (response.status === 401) {
            window.location.href = "login.html";
            return;
        }
        if (!response.ok) {
            showMessage("Could not load your applications. Try again.", false);
            return;
        }
        const data = await response.json();
        applications = data.applications;
        renderBoard();
    } catch (error) {
        showMessage("Cannot reach the server. Is it running?", false);
    }
}


// ---------- Draw the board ----------

// Make the card of ONE application
function makeCard(app) {
    const card = document.createElement("div");
    card.className = "app-card";

    // textContent is safe: it shows text only and never runs HTML
    const company = document.createElement("div");
    company.className = "app-card-company";
    company.textContent = app.company;

    const role = document.createElement("div");
    role.className = "app-card-role";
    role.textContent = app.role;

    card.append(company, role);

    // Date and notes are optional, so only add them when they exist
    if (app.applied_date) {
        const date = document.createElement("div");
        date.className = "app-card-date";
        date.textContent = "Applied " + formatDate(app.applied_date);
        card.append(date);
    }
    if (app.notes) {
        const notes = document.createElement("div");
        notes.className = "app-card-notes";
        notes.textContent = app.notes;
        card.append(notes);
    }

    // Edit and Delete buttons
    const actions = document.createElement("div");
    actions.className = "app-card-actions";

    const editBtn = document.createElement("button");
    editBtn.type = "button";
    editBtn.className = "card-btn";
    editBtn.textContent = "Edit";
    editBtn.addEventListener("click", () => startEdit(app));

    const deleteBtn = document.createElement("button");
    deleteBtn.type = "button";
    deleteBtn.className = "card-btn danger";
    deleteBtn.textContent = "Delete";
    deleteBtn.addEventListener("click", () => deleteApplication(app));

    actions.append(editBtn, deleteBtn);
    card.append(actions);

    return card;
}

// Put every card in its column, and update the small numbers
function renderBoard() {
    for (const stage of STAGES) {
        const list = document.getElementById("list-" + stage);
        const count = document.getElementById("count-" + stage);

        list.innerHTML = "";   // empty the column first

        const inThisStage = applications.filter((app) => app.status === stage);
        for (const app of inThisStage) {
            list.append(makeCard(app));
        }
        count.textContent = inThisStage.length;
    }
}


// ---------- Edit mode ----------

// Fill the form with an application and switch to edit mode
function startEdit(app) {
    editingId = app.id;
    companyInput.value = app.company;
    roleInput.value = app.role;
    statusSelect.value = app.status;
    dateInput.value = app.applied_date || "";
    notesInput.value = app.notes;

    formTitle.textContent = "Edit application";
    saveBtn.textContent = "Save changes";
    cancelBtn.hidden = false;
    showMessage("", false);

    // Move the page up so the user sees the form
    form.scrollIntoView({ behavior: "smooth", block: "start" });
}

// Back to the normal "add" mode, with an empty form
function stopEdit() {
    editingId = null;
    form.reset();
    formTitle.textContent = "Add an application";
    saveBtn.textContent = "Add application";
    cancelBtn.hidden = true;
}


// ---------- Delete ----------
async function deleteApplication(app) {
    // Ask first, because delete cannot be undone
    if (!confirm(`Delete ${app.company} - ${app.role}?`)) return;

    try {
        const response = await fetch("/api/applications/" + app.id, { method: "DELETE" });
        if (response.status === 401) {
            window.location.href = "login.html";
            return;
        }
        if (!response.ok) {
            showMessage("Could not delete. Try again.", false);
            return;
        }
        // If this very application was open in the form, close the form
        if (editingId === app.id) stopEdit();
        await loadApplications();
    } catch (error) {
        showMessage("Cannot reach the server. Is it running?", false);
    }
}


// ---------- Save (add a new one, or save changes) ----------
form.addEventListener("submit", async (event) => {
    event.preventDefault();   // stops the page from reloading

    const company = companyInput.value.trim();
    const role = roleInput.value.trim();

    // Check the two required boxes before sending anything
    if (company === "") {
        showMessage("Please type the company name.", false);
        return;
    }
    if (role === "") {
        showMessage("Please type the role.", false);
        return;
    }

    saveBtn.disabled = true;
    showMessage("Saving...", true);

    // Editing -> PUT to /api/applications/5, adding -> POST to /api/applications
    const isEditing = editingId !== null;
    const url = isEditing ? "/api/applications/" + editingId : "/api/applications";
    const method = isEditing ? "PUT" : "POST";

    try {
        const response = await fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                company: company,
                role: role,
                status: statusSelect.value,
                applied_date: dateInput.value || null,   // empty date -> null
                notes: notesInput.value.trim(),
            }),
        });
        if (response.status === 401) {
            window.location.href = "login.html";
            return;
        }
        if (!response.ok) {
            showMessage("Could not save. Please check your answers.", false);
            return;
        }

        stopEdit();
        showMessage(isEditing ? "Changes saved!" : "Application added!", true);
        await loadApplications();
    } catch (error) {
        showMessage("Cannot reach the server. Is it running?", false);
    } finally {
        saveBtn.disabled = false;
    }
});

// Cancel edit button
cancelBtn.addEventListener("click", () => {
    stopEdit();
    showMessage("", false);
});

// Log out button
document.getElementById("logout-btn").addEventListener("click", async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    window.location.href = "login.html";
});


// ---------- Run when the page opens ----------
loadUser();
loadApplications();