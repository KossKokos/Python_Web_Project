from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class PhotoBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=50)
    url: str = Field(..., max_length=255)


class PhotoModel(PhotoBase):
    class Config:
        orm_mode = True


class PhotoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=50)
    url: Optional[str] = Field(None, max_length=255)


class PhotoUpdateTitle(BaseModel):
    title: str = Field(..., min_length=5, max_length=50)


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=15, default='username')
    email: EmailStr = Field(default='example@gmail.com')
    password: str = Field(min_length=8, max_length=15, default='password')


class UserUpdateTest(BaseModel):
    username: Optional[str]
    email: Optional[str]
    password: Optional[str]
    avatar: Optional[str]


class UserResponce(BaseModel):
    id: int = 1
    username: str = 'username'
    email: EmailStr = 'example@gmail.com'
    password: str = 'password'
    avatar: Optional[str] = None
    role: str = "role"

    class Config:
        orm_mode = True


class ChangePassword(BaseModel):
    new_password: str = Field(min_length=8, max_length=15, default='new_password')


class UserRoleUpdate(BaseModel):
    role: str = "role"