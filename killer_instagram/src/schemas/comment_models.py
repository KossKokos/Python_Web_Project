from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from database import SessionLocal
from users import User
from images import Image


class CommentBase(BaseModel):
    text: str = Field(min_length=5)


class CommentCreate(CommentBase):
    user_id: int  


def check_image_existence(image_id: int) -> bool:
    db = SessionLocal()
    image = db.query(Image).filter(Image.id == image_id).first()
    db.close()
    return image is not None


class Comment(CommentBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True