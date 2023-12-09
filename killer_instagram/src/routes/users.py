from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import service_auth
from src.conf.config import settings
from src.schemas.users import UserResponce

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import session
from repository import user
from database.models import User as UserModel


new_router = APIRouter(prefix="/api/users", tags=["Users"])


@new_router.post("/", response_model=UserModel)
def create_user(username: str, email: str, password: str, db: Session = Depends(session.get_db)):
    db_user = user.create_user(db=db, username=username, email=email, password=password)
    return db_user

@new_router.get("/{user_id}", response_model=UserModel)
def read_user(user_id: int, db: Session = Depends(session.get_db)):
    db_user = user.get_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@new_router.put("/{user_id}", response_model=UserModel)
def update_user(user_id: int, username: str = None, email: str = None, password: str = None, db: Session = Depends(session.get_db)):
    db_user = user.update_user(db=db, user_id=user_id, username=username, email=email, password=password)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@new_router.delete("/{user_id}", response_model=UserModel)
def delete_user(user_id: int, db: Session = Depends(session.get_db)):
    db_user = user.delete_user(db=db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


router = APIRouter(prefix='/users', tags=['users'])


@router.get('/me', response_model=UserResponce)
async def read_users_me(current_user: User = Depends(service_auth.get_current_user)):
    """
    The read_users_me function returns the current user's information.

        get:
          summary: Returns the current user's information.
          description: Returns the current user's information based on their JWT token in their request header.
          responses: HTTP status code 200 indicates success! In this case, it means we successfully returned a User
    
    :param current_user: User: Get the user object of the current user
    :return: The user object
    """
    return current_user


@router.patch('/avatar', response_model=UserResponce)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(service_auth.get_current_user),
                             db: Session = Depends(get_db)):
    """
    The update_avatar_user function updates the avatar of a user.
        Args:
            file (UploadFile): The image to be uploaded as an avatar.
            current_user (User): The user whose avatar is being updated.
            db (Session): A database session for interacting with the database.
    
    :param file: UploadFile: Get the file from the request
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the repository layer
    :return: The updated user
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    r = cloudinary.uploader.upload(file.file, public_id=f'ContactsApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'ContactsApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user