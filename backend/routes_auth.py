import sqlite3
from fastapi import APIRouter,Depends, HTTPException, Request

from database import get_connection
from deps import get_current_user
from schemas import LoginRequest,SignupRequest
from security import hash_password, verify_password

# All routes in this file start with /api/auth
router = APIRouter(prefix="/api/auth", tags =["auth"])

@router.post("/signup",status_code=201)
def signup(data: SignupRequest):
    # Clean the input by removing extra spaces, make email lowercase
    full_name = data.full_name.strip()
    email = data.email.strip().lower()

    # Verify simple email check
    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Please enter a valid email")
    
    conn = get_connection()
    try:
        #  The ? mark are filled in safely by sqlite (this stops sql injection)
        cursor = conn.execute(
            "INSERT INTO users (full_name,email,password_hash) VALUES (?,?,?)",
            (full_name,email,hash_password(data.password)),
        )
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        #  The unique rule on email was broken: this email already exists
        raise HTTPException(status_code=409, detail ="Email already registered")

    finally:
        # Always close the connection, even if there was an error
        conn.close()

    return {"id":user_id,"full_name":full_name,"email":email}



@router.post("/login")
def login(data: LoginRequest, request: Request):
    email = data.email.strip().lower()

    #  Find the user with this email
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE email =?",(email,)).fetchone()
    conn.close()

    # Same message for "no such email" and "wrong password" so nobody can find out which email are registered

    if user is None or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail = "Invalid email or password")

    # Rememeber the user in the signed cookie
    request.session["user_id"] = user["id"]

    return {"id":user["id"], "full_name": user["full_name"],"email":user["email"]}


@router.get("/me")
def me(user = Depends(get_current_user)):
    # Only runs if get_current_user did not stop with a 401
    return {"id":user["id"],"full_name":user["full_name"],"email":user["email"]}

@router.post("/logout")
def logout(request: Request):
    # Forget the user -> clear the signed cookie
    request.session.clear()
    return {"message":"Logged out"}
