from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.schemas.pictures import PhotoUpdate, PhotoModel

from src.repository.pictures import update_picture
from src.database import get_db

router = APIRouter()

@router.put("/photos/{photo_id}", response_model=PhotoModel)
async def update_photo(photo_id: int, body: PhotoUpdate, db: Session = Depends(get_db)):
    photo = update_picture(db, photo_id, body)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    return photo



"""
Тут будуть тільки шляхи: router = APIRouter(prefix='/pictures', tags=['pictures'])

"""