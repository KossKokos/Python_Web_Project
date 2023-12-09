from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import session
from repository import photo
from database.models import Photo as PhotoModel

router = APIRouter(prefix="/api/photos", tags=["Photos"])

@router.post("/", response_model=PhotoModel)
def create_photo(title: str, url: str, db: Session = Depends(session.get_db)):
    db_photo = photo.create_photo(db=db, title=title, url=url)
    return db_photo

@router.get("/{photo_id}", response_model=PhotoModel)
def read_photo(photo_id: int, db: Session = Depends(session.get_db)):
    db_photo = photo.get_photo(db=db, photo_id=photo_id)
    if db_photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    return db_photo

@router.put("/{photo_id}", response_model=PhotoModel)
def update_photo(photo_id: int, title: str, url: str, db: Session = Depends(session.get_db)):
    db_photo = photo.update_photo(db=db, photo_id=photo_id, title=title, url=url)
    if db_photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    return db_photo

@router.delete("/{photo_id}", response_model=PhotoModel)
def delete_photo(photo_id: int, db: Session = Depends(session.get_db)):
    db_photo = photo.delete_photo(db=db, photo_id=photo_id)
    if db_photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    return db_photo
