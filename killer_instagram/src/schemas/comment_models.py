from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from src.database.db import get_db
from src.database.models import User, Image


class CommentBase(BaseModel):
    comment: str = Field(min_length=5)


class CommentCreate(CommentBase):
    # user_id: int  
    image_id: int  
    # parent_comment_id: Optional[int] = None  


    async def check_user_and_image_existence(self):
        user_exists = check_user_existence(self.user_id)
        image_exists = check_image_existence(self.image_id)

        if not user_exists:
            raise ValueError("User does not exist")

        if not image_exists:
            raise ValueError("Image does not exist")


def check_user_existence(user_id: int) -> bool:
    db = get_db()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    return user is not None

def check_image_existence(image_id: int) -> bool:
    db = get_db()
    image = db.query(Image).filter(Image.id == image_id).first()
    db.close()
    return image is not None


class Comment(CommentBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

