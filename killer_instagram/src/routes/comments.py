from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import CommentCreate, Comment
from database import SessionLocal
from services.comment_service import CommentService

"""
Якщо хочете створити шляхи тільки для роботи з коментами, використовуйте цей файл. 
Можна спробувати додати шляхи з коментами до pictures routes, 
так як вони зв'язані, це на ваш вибір
"""

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

comment_service = CommentService(SessionLocal())


@router.post("/comments/", response_model=Comment)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    return comment_service.create_comment(comment)


@router.get("/comments/{comment_id}", response_model=Comment)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    db_comment = comment_service.get_comment(comment_id, db)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment


@router.put("/comments/{comment_id}", response_model=Comment)
def update_comment(comment_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    db_comment = comment_service.update_comment(comment_id, comment, db)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment


@router.delete("/comments/{comment_id}", response_model=Comment)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    db_comment = comment_service.delete_comment(comment_id, db)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment
