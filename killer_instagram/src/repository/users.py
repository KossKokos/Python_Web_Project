from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.users import UserModel

from sqlalchemy.orm import Session
from database.models import User


def create_user(db: Session, username: str, email: str, password: str, avatar: str = None, refresh_token: str = None, confirmed: bool = False):
    user = User(username=username, email=email, password=password, avatar=avatar, refresh_token=refresh_token, confirmed=confirmed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: int, username: str = None, email: str = None, password: str = None, avatar: str = None, refresh_token: str = None, confirmed: bool = None):
    user = get_user(db, user_id)
    if user:
        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.password = password
        if avatar:
            user.avatar = avatar
        if refresh_token:
            user.refresh_token = refresh_token
        if confirmed is not None:
            user.confirmed = confirmed
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user:
        db.delete(user)
        db.commit()
    return user



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


async def update_token(user: User, refresh_token, db: Session) -> None:
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
    return user
    