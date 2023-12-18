from sqlalchemy.orm import Session
from repository.comments import CommentRepository
from schemas import CommentCreate

class CommentService:
    def __init__(self, db: Session):
        self.comment_repo = CommentRepository(db)

    def create_comment(self, comment: CommentCreate):
        return self.comment_repo.create_comment(comment)