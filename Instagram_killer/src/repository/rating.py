from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database.models import Image, Rating
from ..schemas.images import ImageResponse


async def creare_rating(image_id: int, user_id: int, rating: int, db: Session) -> Rating:
    """
    The creare_rating function creates a new rating for an image.
        Args:
            image_id (int): The id of the image to be rated.
            user_id (int): The id of the user who is rating the image.
            rating (int): The value of the rating, between 1 and 5 inclusive.
    
    :param image_id: int: Specify the image that is being rated
    :param user_id: int: Identify the user
    :param rating: int: Set the rating value of the image
    :param db: Session: Pass the database session to the function
    :return: A rating object
    """
    exist_rating = await get_rating_using_id_user_id(image_id=image_id, user_id=user_id, db=db)
    
    if exist_rating:
        return False
    
    new_rating = Rating(
        image_id=image_id,
        user_id=user_id,
        rating=rating
    )
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating


async def get_rating_using_id_user_id(image_id: int, user_id: int, db: Session) -> Rating | None:
    """
    The get_rating_using_id_user_id function returns a Rating object if the image_id and user_id are found in the database.
    Otherwise, it returns None.
    
    :param image_id: int: Filter the ratings by image_id
    :param user_id: int: Filter the rating by user_id
    :param db: Session: Pass the database session to the function
    :return: The rating of a user for an image
    """
    rating = db.query(Rating).filter(Rating.image_id==image_id, Rating.user_id==user_id).first()
    return rating


async def get_rating_using_id(rating_id: int, db: Session) -> Rating | None:
    """
    The get_rating_using_id function returns a rating object using the id of the rating.
        Args:
            rating_id (int): The id of the desired Rating object.
            db (Session): A database session to use for querying data from a database.
        Returns: 
            Rating | None: A Rating object or None if no such item exists in the database.
    
    :param rating_id: int: Filter the query to only return a single rating
    :param db: Session: Pass the database session to the function
    :return: A rating object
    """
    rating = db.query(Rating).filter(Rating.id==rating_id).first()
    return rating


async def get_average_rating_for_image(image: Image, db: Session) -> dict:
    """
    The get_average_rating_for_image function takes an image and a database session as arguments.
    It then queries the database for all ratings associated with that image, calculates the average rating, 
    and returns a dictionary containing both the image and its average rating.
    
    :param image: Image: Pass the image object to the function
    :param db: Session: Pass the database session to the function
    :return: A dictionary with the image and its average rating
    """
    rating = db.query(func.avg(Rating.rating)).filter(Rating.image_id==image.id).first()
    if rating[0] is None:
        return None 
    average_rating = round(rating[0], 2)
    responce_image: ImageResponse = ImageResponse.from_db_model(db_model=image)
    return {"image": responce_image, "rating": average_rating}


async def delete_rating(rating_id: int, db: Session) -> Rating:
    """
    The delete_rating function deletes a rating from the database.
        
    
    :param rating_id: int: Identify which rating to delete
    :param db: Session: Pass the database session to the function
    :return: A rating object
    :doc-author: Trelent
    """
    raiting_to_delete: Rating = db.query(Rating).filter(Rating.id==rating_id).first()
    if not raiting_to_delete:
        return None
    db.delete(raiting_to_delete)
    db.commit()
    return raiting_to_delete

