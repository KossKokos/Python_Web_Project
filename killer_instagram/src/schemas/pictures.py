from typing import List

from pydantic import BaseModel, Field

from src.database.models import Tag, Comment

class PictureModel(BaseModel):

    description: str = Field(max_length=150)
    # url: str = FileUrl()


class PictureResponce(BaseModel):

    id: int
    description: str
    url: str
    user_id: int
    comments: list
    tags: list

    class Config:
        orm_mode = True
