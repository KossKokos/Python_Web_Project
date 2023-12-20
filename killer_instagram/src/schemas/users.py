from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=15, default='username')
    email: EmailStr = Field(default='example@gmail.com')
    password: str = Field(min_length=8, max_length=15, default='password')


class UserResponce(BaseModel):
    id: int = 1
    username: str = 'username'
    email: EmailStr = 'example@gmail.com'
    password: str = 'password'
    avatar: Optional[str] = None
    role: str = "role"
    banned: Optional[bool] = None


    class Config:
        orm_mode = True


class ChangePassword(BaseModel):
    new_password: str = Field(min_length=8, max_length=15, default='new_password')


class UserRoleUpdate(BaseModel):
    role: str = "role"

class BannedUserUpdate(BaseModel):
    banned: bool = False