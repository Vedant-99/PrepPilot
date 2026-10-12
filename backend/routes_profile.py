import json 
from fastapi import APIRouter, Depends

from database import get_connection
from deps import get_current_user
from schemas import ProfileRequest

# Every route in this file starts with /api/profile
router = APIRouter(prefix="/api/profile", tags=["profile"])

# GET /api/profile -> the saved profile of the logged-in user
@router.get("")
def get_profile(user=Depends(get_current_user)):
    conn = get_connection()
    row = conn.execute(
        "SELECT target_role, study_year, skills FROM profiles WHERE user_id=?",
        (user["id"],),
    ).fetchone()
    conn.close()

# No profile yet is normal for a new user so this is not an error
    if row is None:
        return {"profile":None}

    return {
        "profile": {
            "target_role": row["target_role"],
            "study_year": row["study_year"],
            "skills":json.loads(row["skills"]), #text -> python list
        }
    }

#PUT /api/profile -> save the profile(create it , or replace the old ones)
@router.put("")
def save_profile(data: ProfileRequest, user=Depends(get_current_user)):
    conn = get_connection()
    # If this user already has a profile -> update it instead of adding a second one
    conn.execute(
        """
        INSERT INTO profiles (user_id, target_role, study_year, skills)
        VALUES (?,?,?,?)
        ON CONFLICT(user_id) DO UPDATE SET
            target_role = excluded.target_role,
            study_year = excluded.study_year,
            skills = excluded.skills,
            updated_at = CURRENT_TIMESTAMP
        """,
        (user["id"], data.target_role, data.study_year, json.dumps(data.skills)),
        )
    conn.commit()
    conn.close()
    return {"message":"Profile saved"}
