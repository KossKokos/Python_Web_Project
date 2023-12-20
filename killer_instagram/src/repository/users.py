from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.database.models import User, Image, Tag
from src.schemas.users import UserModel, UserRoleUpdate
from src.repository import tags as repository_tags


async def create_user(body: UserModel, db: Session) -> User:
    """
    The create_user function creates a new user in the database.
        

    :param body: UserModel: Deserialize the request body into a usermodel object
    :param db: Session: Access the database
    :return: A user object
    """
    user = User(**body.dict())
    db.add(user)
    db.commit()
    if user.id == 1:
        user.role = "admin"
        db.commit()
    db.refresh(user)
    return user


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user with that email if it exists. If no such user exists,
    it returns None.

    :param email: str: Specify the email of the user we want to get from our database
    :param db: Session: Pass the database session to the function
    :return: A user object or none if the user is not found
    """
    return db.query(User).filter(User.email==email).first()


async def get_user_by_username(username: str, db: Session) -> User | None:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user with that email if it exists. If no such user exists,
    it returns None.

    :param email: str: Specify the email of the user we want to get from our database
    :param db: Session: Pass the database session to the function
    :return: A user object or none if the user is not found
    """
    return db.query(User).filter(User.username==username).first()

async def update_token(user: User, refresh_token: str, db: Session) -> None:
    """
    The update_token function updates the refresh_token for a user in the database.
        Args:
            user (User): The User object to update.
            refresh_token (str): The new refresh token to store in the database.
            db (Session): A SQLAlchemy Session object used to interact with the database.
    
    :param user: User: Get the user's object from the database
    :param refresh_token: Update the refresh_token in the database
    :param db: Session: Access the database
    :return: None
    """
    user.refresh_token = refresh_token
    db.commit()
    db.refresh(user)


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function sets the confirmed field of a user to True.
    
    :param email: str: Get the email address of the user
    :param db: Session: Pass the database session to the function
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def change_password(user: User, new_password: str, db: Session) -> None:
    """
    The change_password function changes the password of a user.
    
    Args:
        user (User): The User object to change the password for.
        new_password (str): The new password to set for this user.
        db (Session): A database session object.
    
    :param user: User: Specify the user whose password is to be changed
    :param new_password: str: Change the password of a user
    :param db: Session: Pass in the database session
    :return: None
    """
    user.password = new_password
    db.commit()
    db.refresh(user)


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.
    
    Args:
        email (str): The email address of the user to update.
        url (str): The URL for the new avatar image.
        db (Session, optional): A database session object.
    
    :param email: Find the user in the database
    :param url: str: The URL for the new avatar image
    :param db: Session: Pass the database session to the function
    :return: A user object
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user


async def get_user_by_id(user_id: int, db: Session) -> User | None:
    """
    The get_user_by_id function returns a User object from the database, given an id.
        Args:
            user_id (int): The id of the user to be retrieved.
            db (Session): A Session instance for interacting with the database.
    
    :param user_id: int: Specify the type of parameter that is expected to be passed in
    :param db: Session: Pass the database session to the function
    :return: A user object or none
    :doc-author: Trelent
    """
    return db.query(User).filter(User.id==user_id).first()


async def change_user_role(user: User, body: UserRoleUpdate, db: Session) -> User:
    """
    The change_user_role function changes the role of a user.
        Args:
            user (User): The User object to change the role of.
            body (UserRoleUpdate): A UserRoleUpdate object containing the new role for this user.
            db (Session): The database session to use when changing this users' role in our database.
    
    :param user: User: Get the user object from the database
    :param body: UserRoleUpdate: Get the role from the request body
    :param db: Session: Access the database
    :return: A user object with updated role
    :doc-author: Trelent
    """
    user.role = body.role
    db.commit()
    db.refresh(user)
    return user
    
    
async def delete_user(user_id: int, db: Session) -> None:
    """
    The delete_user function deletes a user from the database based on the user ID.

    :param user_id: int: ID of the user to be deleted
    :param db: Session: Database session
    :return: None
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return None 

async def get_imagis_quantity(current_user:User, db: Session):
    return 10