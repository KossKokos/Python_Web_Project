from pydantic import BaseModel, Field


class PhotoUpdate(BaseModel):
    title: str = Field(min_length=5, max_length=50, default='title')
    url: str = Field(max_length=255, default='url')


@router.put("/photos/{photo_id}", response_model=PhotoModel)
async def update_photo(photo_id: int, body: PhotoUpdate, db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if body.title:
        photo.title = body.title
    if body.url:
        photo.url = body.url
    
    db.commit()
    db.refresh(photo)
    return photo

