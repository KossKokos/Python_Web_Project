from datetime import datetime

from sqlalchemy.orm import Session

from ..database.models import Comment
from ..schemas import comments as schema_comments


async def add_new_comment(body: schema_comments.CommentModel, user_id: int, db: Session) -> Comment:
    """
    The add_new_comment function creates a new comment in the database.
        Args:
            body (CommentModel): The CommentModel object containing the data to be added to the database.
            user_id (int): The id of the user who is adding this comment.
            db (Session): A connection to the database.
    
    :param body: schema_comments.CommentModel: Validate the data that is sent to the function
    :param user_id: int: Get the user_id from the token
    :param db: Session: Connect to the database
    :return: The comment object, which is the same as the body
    """
    comment: Comment = Comment(
        comment=body.comment,
        image_id=body.image_id,
        user_id=user_id
    )
    db.add(comment)
    db.commit()
    return comment


async def get_comment_by_id(comment_id: int, db: Session) -> Comment | None:
    """
    The get_comment_by_id function returns a comment object from the database based on its id.
        Args:
            comment_id (int): The id of the desired comment.
            db (Session): A connection to the database.
        Returns:
            Comment | None: The requested Comment object or None if it does not exist in the database.
    
    :param comment_id: int: Specify the id of the comment to be returned
    :param db: Session: Pass the database session into the function
    :return: A comment object or none
    """
    exist_comment: Comment = db.query(Comment).filter(Comment.id==comment_id).first()
    return exist_comment


async def update_comment(comment_to_update: Comment, body: schema_comments.CommentUpdate, db: Session) -> Comment:
    """
    The update_comment function updates a comment in the database.
        Args:
            comment_to_update (Comment): The Comment object to update.
            body (schema_comments.CommentUpdate): The new values for the Comment object to be updated with.
            db (Session): A connection to the database.
    
    :param comment_to_update: Comment: Pass in the comment that is to be updated
    :param body: schema_comments.CommentUpdate: Pass the new comment to be updated in the database
    :param db: Session: Access the database
    :return: A comment object
    """
    comment_to_update.comment = body.new_comment
    comment_to_update.updated_at = datetime.now()
    db.commit()
    db.refresh(comment_to_update)
    return comment_to_update


async def delete_comment(comment_to_delete: Comment, db: Session) -> Comment:
    """
    The delete_comment function deletes a comment from the database.
        Args:
            comment_to_delete (Comment): The Comment object to delete.
            db (Session): The database session to use for deleting the Comment object.
        Returns:
            A deleted Comment object.
    
    :param comment_to_delete: Comment: Pass in the comment object that we want to delete
    :param db: Session: Pass the database session to the function
    :return: The deleted comment
    """
    db.delete(comment_to_delete)
    db.commit()
    return comment_to_delete


async def get_comment(comment_id: int, db: Session) -> Comment | None:
    """
    The get_comment function returns a comment object from the database.
        Args:
            comment_id (int): The id of the comment to be returned.
            db (Session): A session object for interacting with the database.
        Returns:
            Comment | None: If a matching comment is found, it will be returned as an instance of Comment; otherwise, None.
    
    :param comment_id: int: Specify the comment id of the comment we want to retrieve from our database
    :param db: Session: Pass in the database session
    :return: A comment object or none
    """
    comment: Comment = db.query(Comment).filter(Comment.id==comment_id).first()
    return comment