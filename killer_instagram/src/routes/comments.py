from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# from database import SessionLocal
from src.schemas.comment_models import CommentCreate, Comment
from src.services.comment_service import CommentService
from src.database.db import get_db
from src.database.models import User, Image
from src.services.auth import service_auth
from src.repository import images as respitory_images


"""
Якщо хочете створити шляхи тільки для роботи з коментами, використовуйте цей файл. 
Можна спробувати додати шляхи з коментами до pictures routes, 
так як вони зв'язані, це на ваш вибір
"""


router = APIRouter(prefix='/images/comments', tags=['comments'])
# db: Session = Depends(get_db)
# comment_service: CommentService = CommentService(db)


@router.post("/", response_model=Comment)
async def create_comment(comment: CommentCreate, 
                   current_user: User = Depends(service_auth.get_current_user),
                   db: Session = Depends(get_db)):
    """
    The create_comment function creates a new comment for an image.
        The function takes in the following parameters:
            - comment: CommentCreate, which is a Pydantic model that contains the information needed to create a new comment. 
                This includes the image_id and text of the comment.
            - current_user: User, which is an object containing information about who made this request (the user). 
                This parameter comes from our service_auth module's get_current_user function, which we pass as Depends(service_auth.get_current-user) to tell FastAPI
    
    :param comment: CommentCreate: Get the comment data from the request body
    :param current_user: User: Get the current user information
    :param db: Session: Get the database session
    :return: A comment object
    """
    image = await respitory_images.get_image_by_id_user_id(image_id=comment.image_id, user_id=current_user.id, db=db)
    if image:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot comment your own image")
    comment_service: CommentService = CommentService(db)
    return await comment_service.create_comment(comment, user_id=current_user.id)


@router.get("/{comment_id}", response_model=Comment)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    db_comment = comment_service.get_comment(comment_id, db)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment


@router.put("/{comment_id}", response_model=Comment)
def update_comment(comment_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    db_comment = comment_service.update_comment(comment_id, comment, db)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment

"""Видаляти коменти не потрібно, в завданні так вказано"""
# @router.delete("/{comment_id}", response_model=Comment)
# def delete_comment(comment_id: int, db: Session = Depends(get_db)):
#     db_comment = comment_service.delete_comment(comment_id, db)
#     if db_comment is None:
#         raise HTTPException(status_code=404, detail="Comment not found")
#     return db_comment

