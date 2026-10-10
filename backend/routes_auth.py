import sqlite3
from fastapi import APIRouter, HTTPException

from database import get_connection
from schemas import SignupRequest
from security import hash_password

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

