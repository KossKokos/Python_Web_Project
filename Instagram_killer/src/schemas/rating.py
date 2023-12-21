from pydantic import BaseModel, Field

from src.database.models import Rating


class RatingModel(BaseModel):
    image_id: int = Field(ge=1)
    rating: int = Field(ge=1, le=5)


class RatingResponse(BaseModel):
    id: int
    image_id: int
    rating: int 

    @staticmethod
    def rewrite_to_responce(rating_db: Rating):
        return RatingResponse(
            id=rating_db.id,
            image_id=rating_db.image_id,
            rating=rating_db.rating
        )
    class Config:
        orm_mode = True

