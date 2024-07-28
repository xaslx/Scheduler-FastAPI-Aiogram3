from pydantic import BaseModel, EmailStr, Field


class GetHelp(BaseModel):
    email: EmailStr
    description: str = Field(min_length=10, max_length=500)
