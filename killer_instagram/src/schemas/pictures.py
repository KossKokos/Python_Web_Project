from pydantic import BaseModel, Field
from typing import Optional


class UserUpdateTest(BaseModel):
    username: Optional[str]
    email: Optional[str]
    password: Optional[str]
    avatar: Optional[str]


class PhotoUpdateTitle(BaseModel):
    title: str = Field(..., min_length=5, max_length=50)


class PhotoBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=50)
    url: str = Field(..., max_length=255)


class PhotoCreate(PhotoBase):
    description: Optional[str] = Field(None, max_length=255)


class PhotoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=50)
    url: Optional[str] = Field(None, max_length=255)


class PhotoUpdateDescription(BaseModel):
    description: Optional[str] = Field(None, max_length=255)


class Photo(PhotoBase):
    id: Optional[int] = None


    class Config:
        orm_mode = True


class PhotoResponse(Photo):
    description: Optional[str]

    class Config:
        orm_mode = True
        


"""
Тут створюйте моделі для фото, наприклад PhotoModel, PhotoResponce, PhotoUpdate, PhotoUpdateDescription і так далі,
приклад у інших файлів 
"""