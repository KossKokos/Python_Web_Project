from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.database.models import Image, Rating, User
from src.repository import images as repository_images
from src.schemas.images import ImageResponse


async def creare_rating(image_id: int, user_id: int, rating: int, db: Session) -> Rating:
    exist_rating = await get_rating_using_id_user_id(image_id=image_id, user_id=user_id, db=db)
    
    if exist_rating:
        return True
    
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
    rating = db.query(Rating).filter(Rating.image_id==image_id, Rating.user_id==user_id).first()
    return rating


async def get_rating_using_id(rating_id: int, db: Session) -> Rating | None:
    rating = db.query(Rating).filter(Rating.id==rating_id).first()
    return rating


async def get_rating_for_image(image: Image, db: Session) -> dict:
    rating = db.query(func.avg(Rating.rating)).filter(Rating.image_id==image.id).first()
    if rating[0] is None:
        return None 
    average_rating = int(rating[0])
    responce_image: ImageResponse = ImageResponse.from_db_model(db_model=image)
    return {"image": responce_image, "rating": average_rating}


async def delete_rating(rating_id: int, db: Session) -> Rating:
    raiting_to_delete: Rating = db.query(Rating).filter(Rating.id==rating_id).first()
    if not raiting_to_delete:
        return None
    db.delete(raiting_to_delete)
    db.commit()
    return raiting_to_delete

