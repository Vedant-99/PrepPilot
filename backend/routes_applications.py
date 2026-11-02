from fastapi import APIRouter, Depends, HTTPException

from database import get_connection
from deps import get_current_user
from schemas import ApplicationRequest

# Every route in this file starts with /api/applications
router = APIRouter(prefix="/api/applications", tags = ["applications"])

#  GET /api/applications  -> All applications of the logged-in user, newest first
@router.get("")
def list_applications(user=Depends(get_current_user)):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, company, role, status, applied_date, notes
        FROM applications
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user["id"],),
    ).fetchall()
    conn.close()
    return {"applications": [dict(row) for row in rows]}

#  POST /api/applications  -> Add one application
#  ApplicationRequest already checked the datea, so bad data never reaches here
@router.post("")
def add_application(data: ApplicationRequest,user=Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO applications (user_id, company, role, status, applied_date, notes)
        VALUES (?,?,?,?,?,?)
        """,
        (user["id"],data.company,data.role,data.status,data.applied_date,data.notes),
    )
    conn.commit()
    new_id = cursor.lastrowid   #   id which database give to new user
    conn.close()
    return {"message": "Application added","id":new_id}

# PUT /api/applications/5 -> change application number 5
# AND user_id = ? makes sure a user can only change their OWN applications
@router.put("/{application_id}")
def update_application(application_id: int, data: ApplicationRequest, user =Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.execute(
        """
        UPDATE applications
        SET company = ? , role = ?, status = ?, applied_date = ?, notes = ?
        WHERE id = ? AND user_id = ?
        """,
        (data.company, data.role, data.status, data.applied_date, data.notes,
         application_id, user["id"]),
    )
    conn.commit()
    changed = cursor.rowcount       # How many rows were changed (0 = not found)
    conn.close()

    if changed == 0:
        raise HTTPException(status_code=404, detail = "Application not found")
    return {"message": "Application updated"}

# DELETE /api/applications/5 -> remove application number 5
@router.delete("/{application_id}")
def delete_application(application_id: int, user=Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.execute(
        "DELETE FROM applications WHERE id = ? AND user_id = ?",
        (application_id,user["id"]),
    )
    conn.commit()
    changed = cursor.rowcount
    conn.close()

    if changed == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": "Application deleted"}
