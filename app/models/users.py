from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserInDB(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
