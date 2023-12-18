from datetime import datetime
from email.mime import image
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from fastapi import UploadFile
from src.database.models import Image


class ImageModel(BaseModel):
    description: str = Field(max_length=150)
    tags: List[str] = []
    upload_time: datetime
    image: Optional[UploadFile] = None

class ImageStatusUpdate(BaseModel):
    done: bool
    transformation_url: Optional[str]
    qr_code_url: Optional[str]
    
class ImageResponse(BaseModel):
    id: int
    user_id: int
    public_id: Optional[str]
    description: Optional[str]
    image_url: Optional[str]

    @staticmethod
    def from_db_model(db_model: Image):
        return ImageResponse(
            id=db_model.id,
            user_id=db_model.user_id,
            description=db_model.description,
            upload_time=db_model.upload_time,
            # image_url=None
            image_url=db_model.image_url,
        )

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "description": "example_description",
                "image_url": "https://example.com/image.jpg",
            }
        }
