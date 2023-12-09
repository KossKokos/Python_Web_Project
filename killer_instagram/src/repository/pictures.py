from typing import List

from sqlalchemy.orm import Session

from src.schemas.pictures import PictureModel
from src.database.models import Picture, User, Tag, Comment


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