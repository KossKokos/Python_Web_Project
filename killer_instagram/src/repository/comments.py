from sqlalchemy.orm import Session
from database.models import CommentDB
from schemas import CommentCreate

"""
тут crud операції тільки над коментами 
"""

class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_comment(self, comment: CommentCreate):
        db_comment = CommentDB(**comment.dict())
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment