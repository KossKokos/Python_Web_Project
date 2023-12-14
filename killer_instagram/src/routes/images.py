from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Query, Body
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.services.auth import service_auth
from src.repository import images as repository_images
from src.schemas.images import ImageModel, ImageResponse, ImageStatusUpdate
from src.database.models import User
from src.database.database import db_transaction
from typing import List
from src.services.cloudinary import CloudImage

router = APIRouter(prefix='/images', tags=['images'])


@router.post("/", response_model=ImageResponse)
async def upload_image(
    description: str,
    tags: List[str] = Query(..., description="List of tags. Use existing tags or add new ones."),
    file: UploadFile = File(...),
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
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

    # Tag limit check
    if len(tags) > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Too many tags. Maximum is 5.")

    try:
        file_extension = file.filename.split(".")[-1]
        image_path = f"images/{current_user.id}_{description}_original.{file_extension}"

        # Save the file
        with open(image_path, "wb") as f:
            f.write(file.file.read())

        # Upload the original image to Cloudinary asynchronously
        cloudinary_response = CloudImage.upload_image(image_path, public_id=f"{current_user.id}_{description}")

        # Save image information to the database
        image = await repository_images.create_image(
            db=db,
            user_id=current_user.id,
            description=description,
            image_url=cloudinary_response["secure_url"],
            public_id=cloudinary_response["public_id"],
            tags=tags,
            file_extension=file_extension,
        )

        # Add tags to the image
        for tag_name in tags:
            tag = await repository_images.get_or_create_tag(db=db, tag_name=tag_name)
            await repository_images.add_tag_to_image(db=db, image_id=image.id, tag_id=tag.id)

        # Add tags to the uploaded image on Cloudinary
        CloudImage.add_tags(cloudinary_response["public_id"], tags)

        return image
    except HTTPException as e:
        raise e
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

        # Check if the image exists
        if image is None:
            raise HTTPException(status_code=404, detail="Image not found")

        # Check if the current user has permission to delete the image
        if image.user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Delete image from /images
        await repository_images.delete_image_local(db=db, image=image)

        # Delete image from Cloudinary
        CloudImage.delete_image(public_id=image.public_id)

        # Delete image from the database
        await repository_images.delete_image_from_db(db=db, image_id=image_id)

    return {"message": "Image deleted successfully"}


@router.put("/{image_id}")
async def update_image_description(
    image_id: int,
    description_update: str,
    # description_update: str = Body(..., embed=True), # Якщо потрібно передавати JSON
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the description of an image.

    Args:
        image_id (int): The ID of the image to update.
        description_update (str): The new description for the image.
        current_user (User): The current user performing the update operation.
        db (Session): The database session.

    Returns:
        ImageResponse: The updated image.
    """
    try:
        # Retrieve image from the database
        image = await repository_images.get_image_by_id(db=db, image_id=image_id)

        # Check if the image exists
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        # Check if the current user has permission to update the image
        if image.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Permission denied")

        # Update image description in the database
        image = await repository_images.update_image_in_db(db=db, image_id=image_id, new_description=description_update)

        # Asynchronously update image information on Cloudinary
        CloudImage.update_image_description_cloudinary(image.public_id, description_update)

        return image
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}",
        )


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

@router.post("/remove_object/{image_id}")
async def remove_object_from_image(
    image_id: int,
    prompt: str,
    db: Session = Depends(get_db),
):
    image = await repository_images.get_image_by_id(db=db, image_id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    transformed_image = CloudImage.remove_object(image.image_url, prompt)
    transformation_url = transformed_image['secure_url']

    # Save transformed image information to the database
    await repository_images.create_transformed_image_link(
        db=db,
        image_id=image.id,
        transformation_url=transformation_url,
        qr_code_url="",  # You can generate a QR code here if needed
    )

    return ImageStatusUpdate(done=True)

@router.post("/apply_rounded_corners/{image_id}")
async def apply_rounded_corners_to_image(
    image_id: int,
    width: int,
    height: int,
    db: Session = Depends(get_db),
):
    image = await repository_images.get_image_by_id(db=db, image_id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    transformed_image = CloudImage.apply_rounded_corners(image.image_url, width, height)
    transformation_url = transformed_image['secure_url']

    # Save transformed image information to the database
    await repository_images.create_transformed_image_link(
        db=db,
        image_id=image.id,
        transformation_url=transformation_url,
        qr_code_url="",  # You can generate a QR code here if needed
    )

    return ImageStatusUpdate(done=True)

@router.post("/improve_photo/{image_id}")
async def improve_photo(
    image_id: int,
    db: Session = Depends(get_db),
):
    image = await repository_images.get_image_by_id(db=db, image_id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    transformed_image = CloudImage.improve_photo(image.image_url)
    transformation_url = transformed_image['secure_url']

    # Save transformed image information to the database
    await repository_images.create_transformed_image_link(
        db=db,
        image_id=image.id,
        transformation_url=transformation_url,
        qr_code_url="",  # You can generate a QR code here if needed
    )

    return ImageStatusUpdate(done=True)
