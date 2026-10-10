// Where we go after the successfull login 
const AFTER_LOGIN_PAGE = "index.html";

//  Helpers -> used by both forms

// Send JSON to the server and return the result
async function postJson(url,body){
    const response = await fetch(url,{
        method:"POST",
        headers: {"Content-Type":"application/json" },
        body: JSON.stringify(body), 
    });
    const data = await response.json().catch(() => ({}));
    return { ok: response.ok, data:data};
}

// Shows a message under the form -> red for errors green for isSuccess is true
function showMessage(text,isSuccess=false){
    const message = document.getElementById("form-message");
    message.textContent = text;
    message.classList.toggle("success",isSuccess);
}

// Turn server's error into a sentence user can understand
function getErrorText(result){
    const detail = result.data.detail;
    if(typeof detail === "string"){
        return detail;
    }
    return "Please check your details and try again"
}


// Signup Form 

const signupForm = document.getElementById("signup-form");
if(signupForm) {
    signupForm.addEventListener("submit", async (event) => {
        //  Stops browser from reloading the page
        event.preventDefault();

        const fullName = document.getElementById("full-name").value.trim();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById("confirm-password").value;

        // check input before sending it to server
        if(fullName.length<2){
            showMessage("Please enter your full name.");
            return;
        }
        if(!email){
            showMessage("Please enter your email.");
            return;
        }
        if(password.length<6){
            showMessage("Password must be at least 6 characters.");
            return;
        }
        if(password !== confirmPassword){
            showMessage("Passwords do not match.");
            return;
        }

        // Disable the button so that user can not click twice
        const button = signupForm.querySelector("button");
        button.disabled = true;

        try{
            const result = await postJson("/api/auth/signup", {
                full_name: fullName,
                email: email,
                password: password,  
            });
            if(result.ok) {
                showMessage("Account created! Taking you to login...", true);
                setTimeout(()=> {
                    window.location.href ="login.html";
                },1000);
            } else {
                showMessage(getErrorText(result));
            }
        } catch (error) {
            showMessage("Cannot reach the server. Is it running?");
        } finally {
            button.disabled = false;
        }
    });
}


//  Login Form
const loginForm = document.getElementById("login-form");

if(loginForm){
    loginForm.addEventListener("submit", async (event) => {
        // Stop browser from reloading the page
        event.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;

        if(!email || !password) {
            showMessage("Please enter your email and password");
            return;
        }
        // Disable the button so the user cannot click twice
        const button= loginForm.querySelector("button");
        button.disabled = true;

        try{
            const result = await postJson("/api/auth/login", {
                email:email,
                password:password,
            });

            if(result.ok){
                showMessage(`Welcome back, ${result.data.full_name}!`, true);
                setTimeout(()=> {
                    window.location.href = AFTER_LOGIN_PAGE;
                }, 500);
            } else {
                showMessage(getErrorText(result));
            }
        } catch (error){
            showMessage("Cannot reach the server. Is it running?");
        } finally {
            button.disabled = false;
        }
    });
    
}