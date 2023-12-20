from sqlalchemy.orm import Session

from src.database.models import Comment
from src.repository.comments import CommentRepository
from src.schemas.comment_models import CommentCreate

class CommentService:
    def __init__(self, db: Session):
        self.comment_repo = CommentRepository(db)

    async def create_comment(self, comment: CommentCreate, user_id: int) -> Comment:
        return self.comment_repo.create_comment(comment, user_id)