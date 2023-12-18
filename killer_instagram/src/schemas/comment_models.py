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
    image_id: int  
    parent_comment_id: Optional[int] = None  


    def check_user_and_image_existence(self):
        user_exists = check_user_existence(self.user_id)
        image_exists = check_image_existence(self.image_id)

        if not user_exists:
            raise ValueError("User does not exist")

        if not image_exists:
            raise ValueError("Image does not exist")


def check_user_existence(user_id: int) -> bool:
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    return user is not None

def check_image_existence(image_id: int) -> bool:
    db = SessionLocal()
    image = db.query(Image).filter(Image.id == image_id).first()
    db.close()
    return image is not None


class Comment(CommentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True