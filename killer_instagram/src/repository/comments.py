from sqlalchemy.orm import Session
from src.database.models import Comment
from src.schemas.comment_models import CommentCreate

"""
тут crud операції тільки над коментами 
"""

class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_comment(self, comment: CommentCreate, user_id: int) -> Comment:
        db_comment = Comment(**comment.dict())
        db_comment.user_id = user_id
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment