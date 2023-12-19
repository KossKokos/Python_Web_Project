from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.services.auth import service_auth
from src.repository import images as repository_images
from src.database.models import User, Image, Rating
from src.database.db import db_transaction
from typing import List
from src.services.roles import RoleRights
from src.services.logout import logout_dependency
from src.schemas import rating as schema_rating
from src.repository import rating as repository_rating

router = APIRouter(prefix='/images/rating', tags=['rating'])

allowd_operation_any_user = RoleRights(["user", "moderator", "admin"])
allowd_operation_admin_moderator = RoleRights(["admin", "moderator"])


@router.post("/", status_code=status.HTTP_200_OK, 
             dependencies=[Depends(logout_dependency), Depends(allowd_operation_any_user)],
             response_model=schema_rating.RatingResponse
             )
async def rate_image(body: schema_rating.RatingModel, 
                     current_user: User = Depends(service_auth.get_current_user),
                     db: Session = Depends(get_db)):
    """
    The rate_image function allows a user to rate an image.
        The rating is stored in the database and the average rating of all ratings for that image is calculated.
        This function returns a JSON object containing the new average rating.
    
    :param body: schema_rating.RatingModel: Validate the request body
    :param current_user: User: Get the user who is currently logged in
    :param db: Session: Get the database session
    :return: The new rating object created
    """
    image: Image = await repository_images.get_image_by_id(db=db, image_id=body.image_id)    
    if not image:
        raise HTTPException(status_code=404, detail="Image doesn't exist")
    if image.user_id == current_user.id:
        raise HTTPException(status_code=403, detail="You can't rate your own image")
    new_rating = await repository_rating.creare_rating(image_id=body.image_id, user_id=current_user.id, rating=body.rating, db=db)
    if new_rating is True:
        raise HTTPException(status_code=403, detail="You have already rated this image before")
    return new_rating


@router.get("/{image_id}", status_code=200,
            dependencies=[Depends(logout_dependency), Depends(allowd_operation_any_user)])
async def get_rating(image_id: int, 
                     current_user: User = Depends(service_auth.get_current_user),
                     db: Session = Depends(get_db)):
    """
    The get_rating function returns the average rating for a given image.
        The function takes an image_id as input and returns the average rating of that image.
        If no ratings have been made yet, it will return a message saying so.
    
    :param image_id: int: Get the image id from the request
    :param current_user: User: Get the user that is currently logged in
    :param db: Session: Get the database session
    :return: A dictionary with the message key
    """
    image: Image = await repository_images.get_image_by_id(db=db, image_id=image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="Image doesn't exist yet")
    average_rating = await repository_rating.get_rating_for_image(image=image, db=db)
    if average_rating is None:
        return {"message": "This image doesn't have rating yet"} 
    return average_rating


@router.delete("/{rating_id}", status_code=200,
               dependencies=[Depends(logout_dependency), Depends(allowd_operation_admin_moderator)],)
            #    response_model=schema_rating.RatingResponse)
async def delete_rating(rating_id: int, 
                        current_user: User = Depends(service_auth.get_current_user),
                        db: Session = Depends(get_db)):
    rating_to_delete: Rating = await repository_rating.delete_rating(rating_id=rating_id, db=db)
    if not rating_to_delete:
        raise HTTPException(status_code=404, detail="Rating not found")
    return {"Deleted raiting": rating_to_delete}
    