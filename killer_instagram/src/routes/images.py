from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.services.auth import service_auth
from src.repository import images as repository_images
from src.schemas.images import ImageModel, ImageResponse
from src.database.models import User
from src.database.database import db_transaction
from typing import List
from src.services.cloudinary import upload_to_cloudinary

router = APIRouter(prefix='/images', tags=['images'])


@router.post("/", response_model=ImageResponse)
async def upload_image(
    description: str,
    tags: List[str] = Query(..., description="List of tags. Use existing tags or add new ones."),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    # TODO  current_user
    # current_user: User = Depends(service_auth.get_current_user),

    """
    Create an image with description and optional tags.

    Args:
        file (UploadFile): The image file to be uploaded.
        description (str): The description for the image.
        tags (List[str]): List of tags for the image.
        current_user (User): The current user uploading the image.
        db (Session): The database session.

    Returns:
        ImageResponse: The created image.
    """

    try:
        file_extension = file.filename.split(".")[-1]
        image_path = f"images/{1}_{description}_original.{file_extension}"
        # TODO  current_user image_path
        # image_path = f"images/{current_user.id}_{description}_original.{file_extension}"

        try:
            with open(image_path, "wb") as f:
                f.write(file.file.read())
        except FileNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error opening file: {str(e)}",
            )
        # Upload the original image to Cloudinary asynchronously
        cloudinary_response = await upload_to_cloudinary(image_path)

        # Save image information to the database
        image = await repository_images.create_image(
            db=db,
            # TODO  current_user
            # user_id=current_user.id,
            user_id=1,
            description=description,
            image_url=cloudinary_response["secure_url"],
            public_id=cloudinary_response["public_id"],
            tags=tags,
        )

        # Add tags to the image
        if tags:
            for tag_name in tags:
                tag = await repository_images.get_or_create_tag(db=db, tag_name=tag_name)
                await repository_images.add_tag_to_image(db=db, image_id=image.id, tag_id=tag.id)

        return image
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}",
        )


@router.delete("/{image_id}")
async def delete_image(
    image_id: int,
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an image by its ID.

    Args:
        image_id (int): The ID of the image to delete.
        current_user (User): The current user performing the delete operation.
        db (Session): The database session.

    Returns:
        dict: Confirmation message.
    """
    with db_transaction(db):
        image = await repository_images.get_image_by_id(db=db, image_id=image_id)

        # Check if the current user has permission to delete the image
        if image.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")

        # TODO deletion logic here (e.g., delete from filesystem or cloud storage)
        # Handle errors during deletion
        try:
            delete_image_from_storage(image.image_url)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting image: {str(e)}",
            )

        # Delete image tags
        await repository_images.delete_image_tags(db=db, image_id=image_id)

        # Delete image from the database
        await repository_images.delete_image(db=db, image_id=image_id)

    return {"message": "Image deleted successfully"}


@router.put("/{image_id}")
async def update_image_description(image_id: int, description: str, current_user: User = Depends(service_auth.get_current_user),
                                   db: Session = Depends(get_db)):
    """
    Update the description of an image.

    Args:
        image_id (int): The ID of the image to update.
        description (str): The new description for the image.
        current_user (User): The current user performing the update operation.
        db (Session): The database session.

    Returns:
        ImageResponse: The updated image.
    """
    image = repository_images.get_image_by_id(db=db, image_id=image_id)

    # Check if the current user has permission to update the image
    if image.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Update image description in the database
    image = repository_images.update_image_description(db=db, image_id=image_id, description=description)

    return image


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(image_id: int, db: Session = Depends(get_db)):
    """
    Get an image by its ID.

    Args:
        image_id (int): The ID of the image to retrieve.
        db (Session): The database session.

    Returns:
        ImageResponse: The retrieved image.
    """
    image = await repository_images.get_image_by_id(db=db, image_id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Assuming that you have a function to convert the database model to the response model
    image_response = ImageResponse.from_db_model(image)

    return image_response

