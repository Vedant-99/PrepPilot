from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator

class SignupRequest(BaseModel):
    # The data signup page sends to the server
    full_name: str =Field(min_length=2, max_length=60)
    email: str =Field(max_length=120)
    password: str = Field(min_length=6, max_length=100)

class LoginRequest(BaseModel):
    # The data the login page sends to the server
    email: str
    password: str

# What the profile form is allowed to send
class ProfileRequest(BaseModel):
    # Only these roles are accepted (same as the dropdown)
    target_role: Literal[
        "Frontend Developer",
        "Backend Developer",
        "Full Stack Developer",
        "Software Engineer",
        "Data Analyst",
    ]
    study_year: int = Field(ge=0, le=4)         # 0 = already graduated
    skills: list[str] = Field(max_length=30)    # at most 30 skills

    # Clean the skills list: trim spaces, drop duplicates (AWS = aws)
    @field_validator("skills")
    @classmethod
    def clean_skills(cls, skills):
        cleaned = []
        seen = set()
        for skill in skills:
            skill = skill.strip()
            if not skill or len(skill) > 30:
                raise ValueError("Each skill must be 1 to 30 characters")
            if skill.lower() not in seen:
                seen.add(skill.lower())
                cleaned.append(skill)
        return cleaned

#  What the mock interview page sends when a round is finished
class AttemptRequest(BaseModel):
    # all means user did not pick a category/ difficulty 
    category: Literal["all","technical","dsa","hr"]
    difficulty: Literal["all","easy","medium","hard"]

    questions_count: int = Field(ge=1,le=20) #atleast 1 question in a round
    points_ticked: int = Field(ge=0,le=200) # key points the user ticked
    points_total: int = Field(ge=0,le=200) # key points that were shown

    # Ticked points can never be more than total points
    @model_validator(mode="after")
    def check_points(self):
        if self.points_ticked > self.points_total:
            raise ValueError("points_ticked cannot be more than points_total")
        return self