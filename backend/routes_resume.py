import io
import re

from fastapi import APIRouter, Depends, File, Form , HTTPException, UploadFile
from pypdf import PdfReader

from deps import get_current_user
from role_skills import ROLE_SKILLS, SKILL_ALIASES

# Every route in this file starts with /api/resume
router = APIRouter(prefix="/api/resume", tags = ["resume"])

MAX_BYTES = 2 * 1024 * 1024     # biggest PDF accepted: 2MB
MAX_PAGES = 10

# Take the PDF bytes and return the text inside it
# The PDF is only read in memory, it is never saved

def extract_text(data):
    encrypted = False
    parts = []
    try:
        reader = PdfReader(io.BytesIO(data))
        encrypted = reader.is_encrypted
        if not encrypted:
            for index, page in enumerate(reader.pages):
                if index >= MAX_PAGES:
                    break
                parts.append(page.extract_text() or "")
    except Exception:
        # A broken or strange PDF -> a clear message not a crash
        raise HTTPException(status_code=400, detail="We could not read this PDF. Try exporting it again.")

    if encrypted:
        raise HTTPException(status_code=400, detail="This PDF is password protected. Please upload an unlocked copy.")
    return "\n".join(parts)

#  Is this skill in the text? We look for each of its words (aliases)
def skill_in_text(skill,text):
    for alias in SKILL_ALIASES[skill]:
        # The letters before and after must NOT be a letter or digit or a dot before is also refused
        # So "java" is NOT found inside "javascript" and "git" is NOT found inside "github"
        pattern = r"(?<![a-z0-9.])" + re.escape(alias) + r"(?![a-z0-9])"
        if re.search(pattern, text):
            return True
    return False

# Split the skills of a role into "found in the resume" and "missing"
def find_skills(text,role):
    text = text.lower()
    found = []
    missing = []
    for skill in ROLE_SKILLS[role]:
        if skill_in_text(skill, text):
            found.append(skill)
        else:
            missing.append(skill)
    return found, missing


# POST /api/resume/check  -> the user sends a PDF and a role, we send back the result
# Form(...) and File(...) mean the data arrives as an upload form, not as JSON
@router.post("/check")
async def check_resume(
    target_role: str = Form(...),
    file: UploadFile = File(...),
    user = Depends(get_current_user),
):
    if target_role not in ROLE_SKILLS:
        raise HTTPException(status_code=400, detail="Please choose a valid target role.")

    # Read one byte more than the limit, so we can tell if the file is too big
    data = await file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="The PDF is too big. The maximum size is 2 MB.")

    # Every real PDF starts with these 4 letters
    if not data.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    text = extract_text(data)
    if len(text.strip()) < 30:
        raise HTTPException(
            status_code=400, 
            detail="This PDF has no readable text. It may be a scanned image. Please use a PDF exported from Word or Google Docs.",
            )

    found, missing = find_skills(text, target_role)
    return {
        "role": target_role,
        "total":len(ROLE_SKILLS[target_role]),
        "found": found,
        "missing":missing,
    }
    