from sqlalchemy.orm import Session
from database.models import Photo

def create_photo(db: Session, title: str, url: str):
    photo = Photo(title=title, url=url)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo

def get_photo(db: Session, photo_id: int):
    return db.query(Photo).filter(Photo.id == photo_id).first()

def update_photo(db: Session, photo_id: int, title: str, url: str):
    photo = get_photo(db, photo_id)
    if photo:
        photo.title = title
        photo.url = url
        db.commit()
        db.refresh(photo)
    return photo

def delete_photo(db: Session, photo_id: int):
    photo = get_photo(db, photo_id)
    if photo:
        db.delete(photo)
        db.commit()
    return photo
