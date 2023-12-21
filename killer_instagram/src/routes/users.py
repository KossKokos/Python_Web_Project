from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import service_auth
from src.schemas.users import UserResponce
from src.services import (
    roles as service_roles,
    logout as service_logout,
    banned as service_banned,
    cloudinary as service_cloudinary
)


router = APIRouter(prefix='/users', tags=['users'])
security = HTTPBearer()

allowd_operation = service_roles.RoleRights(["user", "moderator", "admin"])
allowd_operation_by_admin = service_roles.RoleRights(["admin"])


@router.get('/',
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(service_logout.logout_dependency), 
                          Depends(allowd_operation),
                          Depends(service_banned.banned_dependency)]
            )
async def get_all_usernames(current_user: User = Depends(service_auth.get_current_user),
                            db: Session = Depends(get_db)):
    """
    The get_all_usernames function returns a list of all usernames in the database.
    
    :param current_user: User: Get the current user from the database
    :param db: Session: Get the database session from the dependency injection
    :return: A list of all the usernames in the database
    """
    usernames = await repository_users.return_all_users(db)
    return usernames


@router.get('/me', response_model=UserResponce,
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(service_logout.logout_dependency), 
                          Depends(allowd_operation),
                          Depends(service_banned.banned_dependency)]
            )
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


@router.get('/{username}', 
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(service_logout.logout_dependency), 
                          Depends(allowd_operation),
                          Depends(service_banned.banned_dependency)],
            description = "Any User")
async def get_user_profile(username, 
                           current_user: User = Depends(service_auth.get_current_user),
                           db: Session = Depends(get_db)):
    """
    The get_user_profile function returns a user profile by username.
        Args:
            username (str): The name of the user to get.
    
    :param username: Get the username
    :param current_user: User: Get the current user from the database
    :param db: Session: Get the database connection
    :return: A dictionary
    """
    
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
                    "quantity_of_loaded_images": quantity_of_loaded_images,
                    }

    return user_profile


@router.patch('/avatar', response_model=UserResponce, 
                        status_code=status.HTTP_200_OK,
                        dependencies=[Depends(service_logout.logout_dependency), 
                                      Depends(allowd_operation),
                                      Depends(service_banned.banned_dependency)],
                        )
async def update_avatar_user(file: UploadFile = File(), 
                             current_user: User = Depends(service_auth.get_current_user),
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
  
    public_id = service_cloudinary.CloudImage.generate_name_avatar(email=current_user.email)
    print (114, public_id)
    cloud = service_cloudinary.CloudImage.upload_avatar(file=file.file, public_id=public_id)
    url = service_cloudinary.CloudImage.get_url(public_id=public_id, cloud=cloud)

    user = await repository_users.update_avatar(current_user.email, url=url, db=db)
    return user

@router.patch('/ban/{user_id}', 
                        response_model=UserResponce, 
                        status_code=status.HTTP_200_OK,
                        dependencies=[Depends(service_logout.logout_dependency), 
                                      Depends(allowd_operation_by_admin)],
                        )
async def update_banned_status(user_id:str,
                                credentials: HTTPAuthorizationCredentials = Security(security), 
                                current_user: User = Depends(service_auth.get_current_user),
                                db: Session = Depends(get_db)):
    """
    The update_banned_status function updates the banned status of a user.
        Only admin can ban the user.
        User cannot change own banned status.
        Superadmin status cannot be changed.
    
    :param user_id:str: Get the user_id from the url
    :param body: BannedUserUpdate: Get the banned status from the request body
    :param current_user: User: Get the user who is currently logged in
    :param db: Session: Access the database
    :return: The user object
    """

    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id == user.id:
        raise HTTPException(status_code=403, detail="Permission denied. User cannot change own banned status.")
    if user.id == 1:
        raise HTTPException(status_code=403, detail="Permission denied.Superadmin status cannot be changed.")

    await repository_users.update_banned_status(user, db)
    return user

@router.patch('/unban/{user_id}', 
                        response_model=UserResponce, 
                        status_code=status.HTTP_200_OK,
                        dependencies=[Depends(service_logout.logout_dependency), 
                                      Depends(allowd_operation_by_admin)],
                        )
async def update_unbanned_status(user_id:str,
                                credentials: HTTPAuthorizationCredentials = Security(security), 
                                current_user: User = Depends(service_auth.get_current_user),
                                db: Session = Depends(get_db)):
    """
    The update_banned_status function updates the banned status of a user.
        Only admin can ban the user.
        User cannot change own banned status.
        Superadmin status cannot be changed.
    
    :param user_id:str: Get the user_id from the url
    :param body: BannedUserUpdate: Get the banned status from the request body
    :param current_user: User: Get the user who is currently logged in
    :param db: Session: Access the database
    :return: The user object
    """

    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id == user.id:
        raise HTTPException(status_code=403, detail="Permission denied. User cannot change own banned status.")
    if user.id == 1:
        raise HTTPException(status_code=403, detail="Permission denied.Superadmin status cannot be changed.")

    await repository_users.update_unbanned_status(user, db)
    return user

@router.delete('/{user_id}',
               status_code=status.HTTP_200_OK,
               dependencies=[Depends(service_logout.logout_dependency), 
                             Depends(allowd_operation_by_admin)])
async def delete_user(user_id: int, current_user: User = Depends(service_auth.get_current_user),
                      db: Session = Depends(get_db)):
    """
    The delete_user function allows an admin to delete a user.

    :param user_id: int: ID of the user to be deleted
    :param current_user: User: Get the current user from the database
    :param db: Session: Database session
    :return: HTTP status 204 (No Content)
    """
 
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
      
    if current_user.id != 1 and user.role == "admin":
        raise HTTPException(status_code=403, detail="Permission denied. Only supreadmin can delede other admin.")
    
    if current_user.id == user_id:
        raise HTTPException(status_code=403, detail="Permission denied. Cannot delete own account.")
    
    if user.id == 1:
        raise HTTPException(status_code=403, detail="Permission denied. Superadmin user cannot be deleted.")

    await repository_users.delete_user(user_id, db)
    return {"message": f"User {current_user.email} successfully deleted"}