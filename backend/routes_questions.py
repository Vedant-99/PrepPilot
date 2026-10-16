from typing import Optional
from fastapi import APIRouter, Depends

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
