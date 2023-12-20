from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from src.database.db import get_db
from src.database.models import User, Image

from comment_models import PydanticUser 
from comment_models import get_comment_by_id, delete_comment_from_db


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
        

class PydanticUser(BaseModel):
    username: str
    is_admin: bool
    is_moderator: bool


async def delete_comment(comment_id: int, current_user: PydanticUser):
    comment = get_comment_by_id(comment_id) 

    if current_user.is_admin or current_user.is_moderator:
        delete_comment_from_db(comment_id)
        return "Comment deleted successfully"
    else:
        return "You don't have permission to delete this comment"




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

