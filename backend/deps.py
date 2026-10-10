from fastapi import HTTPException, Request
from database import get_connection

def get_current_user(request: Request):
    #  Read the user id from the signed cookie
    user_id = request.session.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401,detail="Please log in")

    # Load that user from database if exits
    conn = get_connection()
    user = conn.execute(
        "SELECT id, full_name, email FROM users WHERE id =?",(user_id,)
    ).fetchone()
    conn.close()

    # The cookie points to the user that no longer exists:
    if user is None:
        request.session.clear()
        raise HTTPException(status_code=401,detail="Please log in")
    
    return user