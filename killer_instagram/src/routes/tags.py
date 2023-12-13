from fastapi import APIRouter, Depends, Depends, HTTPException, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.services.auth import service_auth
from src.repository import images as repository_images
from src.schemas.images import ImageModel, ImageResponse
from src.database.models import User
from typing import List
from src.services.cloudinary import upload_to_cloudinary

router = APIRouter(prefix='tags', tags=['tags'])

"""
Якщо хочете створити шляхи тільки для роботи з тегами, використовуйте цей файл. 
Можна спробувати додати шляхи з тегами до pictures routes, 
так як вони зв'язані, це на ваш вибір
"""

@router.get("/tags", response_model=List[str])
async def get_existing_tags(db: Session = Depends(get_db)):
    existing_tags = await repository_images.get_existing_tags(db)
    return existing_tags
