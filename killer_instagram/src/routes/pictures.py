from typing import List

from fastapi import (
    APIRouter, 
    Depends, 
    Depends, 
    HTTPException, 
    status, 
    Security, 
    BackgroundTasks, 
    Request,
    UploadFile, 
    File
)
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from fastapi import APIRouter, HTTPException
from starlette.responses import StreamingResponse
from src.services.auth import service_auth
from src.services.cloud_photos import CloudImage
from src.database.db import get_db
from src.database.models import User, Picture
from src.repository import pictures as repository_pictures
from src.schemas import pictures as schema_picture

router = APIRouter(prefix='/pictures', tags=['pictures'])
security = HTTPBearer()


@router.post('/',response_model=schema_picture.PictureResponce,
                status_code=status.HTTP_201_CREATED)
async def upload_picture(q: schema_picture.PictureModel = Depends(),
                         file: UploadFile = File(), 
                         db: Session = Depends(get_db),
                         current_user: User = Depends(service_auth.get_current_user)):
    body = q.dict()
    public_id = CloudImage.generate_name_picture(email=current_user.email)
    cloud = CloudImage.upload(file=file, public_id=public_id)
    photo_url = CloudImage.get_url(public_id=public_id, cloud=cloud)
    picture = await repository_pictures.create_picture(body=body, url=photo_url, user=current_user, db=db)
    return picture


@router.get('/', #response_model=List[schema_picture.PictureResponce],
                 status_code=status.HTTP_200_OK)
async def read_photos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                      current_user: User = Depends(service_auth.get_current_user)):
    pictures = await repository_pictures.read_pictures(skip=skip, limit=limit, user=current_user, db=db)
    return pictures

@router.get('/transformed/{picture_id}', response_class=StreamingResponse)
async def get_transformed_picture(picture_id: int):
    picture = await repository_pictures.get_picture_by_id(picture_id, db)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")
    
    transformed_url = CloudImage.get_transformed_url(picture.url)
    image_content = CloudImage.download(transformed_url)
    
    return StreamingResponse(content=image_content, media_type="image/jpeg")

@router.get('/qr-code/{picture_id}', response_class=StreamingResponse)
async def get_qr_code(picture_id: int):
    picture = await repository_pictures.get_picture_by_id(picture_id, db)
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")

    qr_code_content = generate_qr_code(picture.url)  #  функція для генерації QR-коду

    return StreamingResponse(content=qr_code_content, media_type="image/png")
