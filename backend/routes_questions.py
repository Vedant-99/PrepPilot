from typing import Optional
from fastapi import APIRouter, Depends, HTTPException

from database import get_connection
from deps import get_current_user

# Every routes in this file starts with /api/questions
router = APIRouter(prefix="/api/questions", tags =["questions"])

# GET /api/questions -> List of questions
@router.get("")
def list_questions(
    category: Optional[str] =None,
    difficulty: Optional[str] =None,
    user = Depends(get_current_user),
):
    # key_points is NOT sent here, so the answer is not shown before the user tries
    sql = "SELECT id, category, topic , difficulty, question FROM questions"

    conditions= []
    values =[]
    if category:
        conditions.append("category= ?")
        values.append(category)
    if difficulty:
        conditions.append("difficulty= ?")
        values.append(difficulty)

    if conditions:
        sql += " WHERE "+ " AND ".join(conditions)
    sql += " ORDER BY id"

    conn = get_connection()
    rows = conn.execute(sql,values).fetchall()
    conn.close()

    return {"questions": [dict(row) for row in rows]}

# GET /api/questions/5/key-points -> the key points of ONE question
# Called only when the user clicks "Show key points"
@router.get("/{question_id}/key-points")
def get_key_points(question_id: int, user=Depends(get_current_user)):
    conn = get_connection()
    row = conn.execute(
        "SELECT key_points FROM questions WHERE id = ?",
        (question_id,),
    ).fetchone()
    conn.close()

    # No question with this id -> 404 means "not found"
    if row is None:
        raise HTTPException(status_code=404, detail="Question not found")

    return {"key_points": row["key_points"]}