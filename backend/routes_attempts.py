from fastapi import APIRouter, Depends

from database import get_connection
from deps import get_current_user
from schemas import AttemptRequest

# Every route in this file starts with /api/attempts
router = APIRouter(prefix="/api/attempts", tags=["attempts"]) 


# POST /api/attempts -> save one finished round of the logged-in user
# AttemptRequest already checked the numbers, so bad data never reaches here
@router.post("")
def save_attempt(data: AttemptRequest, user = Depends(get_current_user)):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO attempts
            (user_id, category, difficulty, questions_count, points_ticked, points_total)
        VALUES (?,?,?,?,?,?)
        """,
        (
            user["id"],
            data.category,
            data.difficulty,
            data.questions_count,
            data.points_ticked,
            data.points_total,
        ),
    )
    conn.commit()
    conn.close()
    return {"message":"Round saved"}


# GET /api/attempts/summary -> totals of the logged-in user for dashboard
@router.get("/summary")
def attempts_summary(user =Depends(get_current_user)):
    conn = get_connection()

    # COALESCE(.....,0) gives 0 instead of NULL when user has no rounds yet
    row = conn.execute(
        """
        SELECT COUNT(*)                             AS rounds,
               COALESCE(SUM(questions_count),0)     AS questions,
               COALESCE(SUM(points_ticked),0)       AS ticked,
               COALESCE(SUM(points_total),0)        AS total,
               MAX(created_at)                      AS last_practiced
        FROM attempts
        WHERE user_id = ?
        """,
        (user["id"],),
    ).fetchone()
    conn.close()

      # Coverage = ticked points out of all points shown, as a percent
    # No points shown yet -> None, so the page can say "no score yet"
    coverage = None
    if row["total"] > 0:
        coverage = round(row["ticked"] * 100 / row["total"])

    return {
        "rounds": row["rounds"],
        "questions": row["questions"],
        "points_ticked": row["ticked"],
        "points_total": row["total"],
        "coverage_percent": coverage,
        "last_practiced": row["last_practiced"],
    }
