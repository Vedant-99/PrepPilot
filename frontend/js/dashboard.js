//  Small helpers

//  Returns "morning", "afternoon", "evening" for the greeting
function getPartOfDay() {
    const hour = new Date().getHours();
    if(hour < 12) return "morning";
    if(hour < 17) return "afternoon";
    return "evening";
}

//  function to get first letter of first 2 words:
function getInitials(fullName) {
    const words = fullName.trim().split(/\s+/);
    const letters = words.slice(0,2).map((word) => word[0]);
    return letters.join("").toUpperCase();
}

//  Fill the pages with the looged-in user's data 
function showUser(user) {
    const firstName = user.full_name.trim().split(/\s+/)[0];

    // textContent is safe: it shows text only and never runs HTML
    document.getElementById("greeting").textContent = `Good ${getPartOfDay()}, ${firstName}`;
    document.getElementById("user-name").textContent = user.full_name;
    document.getElementById("user-email").textContent = user.email;
    document.getElementById("user-initials").textContent = getInitials(user.full_name);
    
    //Today's date :
    document.getElementById("today-date").textContent = new Date().toLocaleDateString("en-GB",{
        weekday:"long",
        day: "numeric",
        month:"long",
    });
}


//  Page start -> who is logged in?

async function loadDashboard() {
    try {
        // the browser sends the login cookie automatically
        const response = await fetch("/api/auth/me");
        
        // 401 -> not logged in so send the visitor to login page
        if(response.status===401){
            window.location.href = "login.html";
            return;
        }
        const user = await response.json();
        showUser(user);
    } catch (error) {
        // Server if off or network failed: 
        document.getElementById("greeting").textContent = "Cannot reach the server. Is it running?";
    }
}

//  Logout button -> clear the session and go to login back:
document.getElementById("logout-btn").addEventListener("click", async () =>{
    await fetch("/api/auth/logout", {method: "POST"});
    window.location.href = "login.html";
});

//  Run when page opens:
loadDashboard();