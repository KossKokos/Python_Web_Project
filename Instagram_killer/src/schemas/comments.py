from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CommentModel(BaseModel):
    comment: str = Field(max_length=100)
    image_id: int = Field(ge=1)


class CommentResponce(BaseModel):
    id: int
    comment: str
    image_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class CommentUpdate(BaseModel):
    new_comment: str = Field(max_length=100)


