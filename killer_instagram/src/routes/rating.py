from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.services.auth import service_auth
from src.repository import images as repository_images
from src.database.models import User, Image, Rating
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
    if new_rating is False:
        raise HTTPException(status_code=403, detail="You have already rated this image before")
    return new_rating


@router.get("/{rating_id}", status_code=200,
            dependencies=[Depends(logout_dependency), Depends(allowd_operation_admin_moderator)])
async def get_rating(rating_id: int, 
                     current_user: User = Depends(service_auth.get_current_user),
                     db: Session = Depends(get_db)):
    """
    The get_rating function returns a rating object given the id of the rating.
        The function takes in an integer as its argument and returns a JSON object containing 
        information about that particular rating.
    
    :param rating_id: int: Get the rating from the database
    :param current_user: User: Get the user who is currently logged in
    :param db: Session: Get a database session from the sessionlocal class
    :return: A dictionary that contains the rating object
    """
    rating: Rating | None = await  repository_rating.get_rating_using_id(rating_id=rating_id, db=db)
    if rating is None:
        raise HTTPException(status_code=404, detail="Rating doesn't exist")
    return {"Rating": rating}


@router.delete("/{rating_id}", status_code=200,
               dependencies=[Depends(logout_dependency), Depends(allowd_operation_admin_moderator)])
async def delete_rating(rating_id: int, 
                        current_user: User = Depends(service_auth.get_current_user),
                        db: Session = Depends(get_db)):
    """
    The delete_rating function deletes a rating from the database.
        The function takes in an integer representing the id of the rating to be deleted, 
        and returns a dictionary containing information about which raiting was deleted.
    
    :param rating_id: int: Find the rating in the database
    :param current_user: User: Get the user that is currently logged in
    :param db: Session: Get the database session
    :return: The deleted rating
    """
    rating_to_delete: Rating = await repository_rating.delete_rating(rating_id=rating_id, db=db)
    if not rating_to_delete:
        raise HTTPException(status_code=404, detail="Rating not found")
    return {"Deleted raiting": rating_to_delete}
    