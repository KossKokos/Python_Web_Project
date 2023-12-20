"""
1.	Створити маршрут для профіля користувача за його унікальним юзернеймом. Повинна повертатися вся інформація про користувача. Імя, коли зарєсттрований, кількість завантажених фото тощо
2.	Користувач може редагувати інформацію про себе, та бачити інформацію про себе. Це мають бути різні маршрути з профілем користувача. Профіль для всіх користувачів, а інформація для себе - це те що можно редагувати
3.	Адміністратор може робити користувачів неактивними (банити). Неактивні користувачі не можуть заходити в застосунок

User ID: A unique identifier for each user in the system.
Username: The name chosen by the user for identification.
Email: User's email address, often used for communication and login purposes.
Password (encrypted): A securely stored and encrypted password for user authentication.
Full Name: User's complete name (first name, last name, etc.).
Date of Birth: User's date of birth.
Profile Picture URL: URL pointing to the user's profile picture or avatar.
Bio/Description: A brief description or biography of the user.
Location: User's geographical location (city, state, country).
Contact Information: Phone number, address, etc. (if applicable and provided).
Social Media Links: Links to the user's social media profiles (Facebook, Twitter, LinkedIn, etc.).
Preferences/Settings: User-specific preferences or settings related to the application or service.
Account Creation Date: Date and time when the user account was created.
Last Login Date: Date and time of the user's last login to the system.
Account Status: Indicates whether the account is active, suspended, or deleted.
Role/Permissions: User's role or level of access within the system (e.g., admin, regular user, moderator).

"""


from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import service_auth
from src.services.cloudinary import CloudImage
from src.conf.config import settings
from src.schemas.users import UserResponce
from src.services.roles import RoleRights
from src.services.logout import logout_dependency
from src.services.cloudinary import CloudImage

router = APIRouter(prefix='/users', tags=['users'])

allowd_operation_get = RoleRights(["user", "moderator", "admin"])


@router.post('/{username}', 
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(logout_dependency), Depends(allowd_operation_get)],
            description = "Any User")
async def get_user_profile(username, current_user: User = Depends(service_auth.get_current_user),
                           db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_username(username, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'User with username: {username} not found.')
    
    quantity_of_loaded_images: int = await repository_users.get_imagis_quantity(user, db)

    user_profile = {
                    "user id": user.id,
                    "username":user.username,
                    "email": user.email,
                    "registrated at":user.created_at,
                    "banned": user.banned,
                    "user role":user.role,
                    "avatar URL": user.avatar,
                    
                    "quantity_of_loaded_images": quantity_of_loaded_images
                    }

    return user_profile



@router.get('/me', response_model=UserResponce,
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(logout_dependency), Depends(allowd_operation_get)],
            description = "Any User")
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


@router.patch('/avatar', response_model=UserResponce, status_code=status.HTTP_200_OK,
                        dependencies=[Depends(logout_dependency), Depends(allowd_operation_get)],
                        description = "Any User")
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