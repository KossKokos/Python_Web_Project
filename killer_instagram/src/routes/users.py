from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import service_auth
from src.services.cloud_photos import CloudImage
from src.conf.config import settings
from src.schemas.users import UserResponce

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/me', response_model=UserResponce, status_code=status.HTTP_202_ACCEPTED)
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


@router.patch('/avatar', response_model=UserResponce, status_code=status.HTTP_200_OK)
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
`    """
    public_id = CloudImage.generate_name_avatar(email=current_user.email)
    cloud = CloudImage.upload(file=file.file, public_id=public_id)
    url = CloudImage.get_url(public_id=public_id, cloud=cloud)

    user = await repository_users.update_avatar(current_user.email, url=url, db=db)
    return user