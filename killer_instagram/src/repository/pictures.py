from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.schemas.pictures import PictureModel
from src.database.models import Picture, User, Tag, Comment
from src.services.auth import service_auth
from src.database.db import get_db
from src.repository import pictures as repository_pictures
from src.schemas import pictures as schema_picture

router = APIRouter(prefix='/pictures', tags=['pictures'])

@router.post('/add_tags/{picture_id}', response_model=schema_picture.PictureResponce,
             status_code=status.HTTP_200_OK)
async def add_tags_to_picture(
    picture_id: int,
    tags: List[str] = Query(..., title="Tags to add"),
    db: Session = Depends(get_db),
    current_user: User = Depends(service_auth.get_current_user)
):
    picture = await repository_pictures.add_tags_to_picture(picture_id, tags, db)
    return picture
    

async def create_picture(body: PictureModel, url: str, user: User, db: Session) -> Picture:
    picture = Picture(description=body.description, url=url, user_id=user.id)
    db.add(picture)
    db.commit()
    db.refresh(picture)
    return picture


async def read_pictures(skip: int, limit: int, user: User, db: Session) -> List[Picture]:
    pictures = db.query(Picture).filter(Picture.user_id==user.id).offset(skip).limit(limit).all()
    for picture in pictures:
        if picture.tags == None:
            picture['tags'] = []
        if picture.comments == None:
            picture.comments = []
    return pictures
