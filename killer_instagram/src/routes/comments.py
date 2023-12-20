from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.models import User, Comment, Image
from src.services.auth import service_auth
from src.database.db import get_db
from src.repository import comments as repository_comments, images as repository_images
from src.schemas import comments as schema_comments
from src.services.roles import RoleRights
from src.services.logout import logout_dependency

router = APIRouter(prefix='/images/comments', tags=['comments'])

allowd_operation_admin= RoleRights(["admin"])
allowd_operation_any_user = RoleRights(["user", "moderator", "admin"])
allowd_operation_delete_user = RoleRights(["admin"])
allowd_operation_admin_moderator = RoleRights(["admin", "moderator"])


@router.post("/", status_code=200, 
             response_model=schema_comments.CommentResponce,
             dependencies=[Depends(logout_dependency), Depends(allowd_operation_any_user)])
async def add_comment(body: schema_comments.CommentModel,
                current_user: User = Depends(service_auth.get_current_user),
                db: Session = Depends(get_db)):
    """
    The add_comment function creates a new comment for an image.
        The function takes in the following parameters:
            body (CommentModel): A CommentModel object containing the information of the comment to be created.
            current_user (User): The user who is making this request, as determined by service_auth.get_current_user().
            db (Session): An SQLAlchemy Session object that will be used to make database queries and commits.
    
    :param body: schema_comments.CommentModel: Validate the body of the request
    :param current_user: User: Get the user that is currently logged in
    :param db: Session: Access the database
    :return: A comment object
    """
    image: Image | None = await repository_images.get_image_by_id(db=db, image_id=body.image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image doesn't exist")
    if image.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You can't comment your own image")
    comment: Comment = await repository_comments.add_new_comment(body=body, user_id=current_user.id, db=db)
    return comment


@router.put("/{comment_id}", status_code=200,
            response_model=schema_comments.CommentResponce,
            dependencies=[Depends(logout_dependency), Depends(allowd_operation_any_user)])
async def update_comment(comment_id: int,
                         body: schema_comments.CommentUpdate,
                         current_user: User = Depends(service_auth.get_current_user),
                         db: Session = Depends(get_db)):
    """
    The update_comment function updates a comment in the database.
        Args:
            comment_id (int): The id of the comment to update.
            body (schema_comments.CommentUpdate): The updated data for the Comment object, as specified by schema_comments.CommentUpdate().
            current_user (User): The user who is making this request, as determined by service_auth.get_current_user().
            db (Session): An SQLAlchemy Session object that will be used to make database queries and commits.

    :param comment_id: int: Get the comment to update
    :param body: schema_comments.CommentUpdate: Get the body of the comment to be updated
    :param current_user: User: Get the current user from the token
    :param db: Session: Pass the database connection
    :return: A comment object
    """
    exist_comment: Comment = await repository_comments.get_comment_by_id(comment_id=comment_id, db=db)
    if not exist_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if exist_comment.user_id != current_user.id and current_user.role not in allowd_operation_admin_moderator.allowed_roles:
        raise HTTPException(status_code=403, detail="You don't have access to update others comments") 
    updated_comment: Comment = await repository_comments.update_comment(comment_to_update=exist_comment, body=body, db=db)
    return updated_comment

