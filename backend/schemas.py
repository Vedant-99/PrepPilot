from pydantic import BaseModel, Field

class SignupRequest(BaseModel):
    # The data signup page sends to the server
    full_name: str =Field(min_length=2, max_length=60)
    email: str =Field(max_length=120)
    password: str = Field(min_length=6, max_length=100)
    