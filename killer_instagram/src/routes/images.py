from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Query, Body
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import StreamingResponse
from io import BytesIO
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.services.auth import service_auth
from src.repository import images as repository_images
from src.repository.images import create_transformed_image_link, get_image_by_id
from src.schemas.images import ImageModel, ImageResponse, ImageStatusUpdate
from src.database.models import User, TransformedImageLink
from src.database.database import db_transaction
from src.repository.tags import get_existing_tags
from typing import List
from src.services.cloudinary import CloudImage
from src.services.qr_code import get_qr_code_url, generate_qr_code, save_qr_code_url_to_db, upload_qr_code_to_cloudinary, save_qr_code_url_to_db

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

        publick_id = CloudImage.generate_name_image(email=current_user.email, filename=file.filename)
        cloudinary_response = CloudImage.upload_image(file=file.file, public_id=publick_id)

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

        # Add new tags to the existing tags list
        existing_tags = await get_existing_tags(db)
        for tag_name in tags:
            if tag_name not in existing_tags:
                existing_tags.append(tag_name)

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
        # await repository_images.delete_image_local(db=db, image=image)

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


@router.get("/transformed_image/{image_id}", response_model=ImageResponse)
async def get_transformed_image(image_id: int, current_user: User = Depends(service_auth.get_current_user), db: Session = Depends(get_db)):
    """
    Get transformed image links by the ID of the original image.

    Args:
        image_id (int): The ID of the original image.
        db (Session): The database session.

    Returns:
        List[TransformedImageLink]: List of transformed image links.
    """
    # Отримати зображення за його ID
    image = await repository_images.get_image_by_id(db=db, image_id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    print(image)
    
    image_response = ImageResponse.from_db_model(image)
    print(image_response)


    # Отримати трансформовані посилання для цього зображення
    links = image_response.transformed_links

    return ImageResponse(
        id=image_response.id,
        user_id=image_response.user_id,
        public_id=image_response.public_id,
        description=image_response.description,
        transformed_links=links,
        image_url=image_response.image_url,
    )


@router.post("/remove_object/{image_id}")
async def remove_object_from_image(
    image_id: int,
    prompt: str = "Star",
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
    # Fetch the original image URL from the database
    image = await repository_images.get_image_by_id(db=db, image_id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        transformed_image = CloudImage.remove_object(image.public_id, prompt)
        transformation_url = transformed_image['secure_url']

        # Check if QR code URL exists in the database
        qr_code_link = await get_qr_code_url(db=db, image_id=image.id)

        if qr_code_link:
            qr_code_url = qr_code_link.qr_code_url
        else:
            qr_code_url = None

        # Save transformed image information to the database
        await repository_images.create_transformed_image_link(
            db=db,
            image_id=image.id,
            transformation_url=transformation_url,
            qr_code_url=qr_code_url,  # You can generate a QR code here if needed
        )

        response_data = {
            "done": True,
            "transformation_url": transformation_url,
            "qr_code_url": qr_code_url,
        }

        return ImageStatusUpdate(**response_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}",
        )


@router.post("/apply_rounded_corners/{image_id}")
async def apply_rounded_corners_to_image(
    image_id: int,
    border: str = "5px_solid_black",
    radius: int = 50,
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
    # Fetch the original image URL from the database
    image = await repository_images.get_image_by_id(db=db, image_id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        transformed_image = CloudImage.apply_rounded_corners(image.public_id, border, radius)
        transformation_url = transformed_image['secure_url']

        # Check if QR code URL exists in the database
        qr_code_link = await get_qr_code_url(db=db, image_id=image.id)

        if qr_code_link:
            qr_code_url = qr_code_link.qr_code_url
        else:
            qr_code_url = None

        # Save transformed image information to the database
        await repository_images.create_transformed_image_link(
            db=db,
            image_id=image.id,
            transformation_url=transformation_url,
            qr_code_url="",  # You can generate a QR code here if needed
        )

        response_data = {
            "done": True,
            "transformation_url": transformation_url,
            "qr_code_url": qr_code_url,
        }

        return ImageStatusUpdate(**response_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}",
        )


@router.post("/improve_photo/{image_id}")
async def improve_photo(
    image_id: int,
    mode: str = 'outdoot',
    blend: int = 100,
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
    image = await repository_images.get_image_by_id(db=db, image_id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
  
    try:
        transformed_image = CloudImage.improve_photo(image.image_url, mode, blend)
        transformation_url = transformed_image['secure_url']
        print(f"Transformed URL: {transformation_url}")

        # Save transformed image information to the database
        await repository_images.create_transformed_image_link(
            db=db,
            image_id=image.id,
            transformation_url=transformation_url,
            qr_code_url="",  # You can generate a QR code here if needed
        )

        return {"done": True, "transformation_url": transformation_url, "qr_code_url": None}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}",
        )


@router.post("/get_link_qrcode/{image_id}")
async def get_transformed_image_link_qrcode(
    image_id: int,
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a link from the database.

    Args:
        image_id (int): The ID of the original image.
        db (Session): The database session.

    Returns:
        dict: The response containing the transformation URL and QR code URL.
    """
    try:
        # Отримати URL та public_id трансформованого зображення
        image = await repository_images.get_image_by_id(db=db, image_id=image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        image_response = ImageResponse.from_db_model(image)

        # Перевірити, чи список не порожній
        if not image_response.transformed_links:
            raise HTTPException(status_code=404, detail="No transformed links found for the image")

        # Отримати перший URL трансформованого зображення
        selected_transformation_url = image_response.transformed_links[0].qr_code_url if image_response.transformed_links else None
        url = image_response.transformed_links[0].transformation_url if image_response.transformed_links else None

        response_data = {
            "transformation_url": url,
            "qr_code_url": selected_transformation_url,
        }

        return response_data
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}",
        )


@router.post("/make_qr_code/{image_id}")
async def make_qr_code_url_for_image(
    image_id: int,
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Make QR code URL for transformed image by original image ID.

    Args:
        image_id (int): The ID of the image.
        db (Session): The database session.

    Returns:
        dict: The QR code URL.
    """
    try:
        # Отримати URL та public_id трансформованого зображення
        image = await repository_images.get_image_by_id(db=db, image_id=image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")

        image_response = ImageResponse.from_db_model(image)
        print(f"image_response:{image_response}")

        # Перевірити, чи список не порожній
        if not image_response.transformed_links:
            raise HTTPException(status_code=404, detail="No transformed links found for the image")

        # Отримати перший URL трансформованого зображення
        selected_transformation_url = image_response.transformed_links[0].transformation_url if image_response.transformed_links else None
        print(f"selected_transformation_url:{selected_transformation_url}")

        # Генерація QR-коду
        qr_code = await generate_qr_code(selected_transformation_url)

        publick_id = CloudImage.generate_name_image(email=current_user.email, filename="qr_code")
        print(f"public_id:{publick_id}")

        # Оновити Cloudinary і зберегти QR-код
        qr_code_publick_id = await upload_qr_code_to_cloudinary(qr_code, public_id=publick_id)
        print(f"qr_code_public_id:{qr_code_publick_id}")

        # Оновити посилання на QR-код в базі даних
        await save_qr_code_url_to_db(
            db=db,
            image_id=image_id,
            transformation_url=selected_transformation_url,
            qr_code_url=qr_code_publick_id,
        )

        return {"qr_code_url": qr_code_publick_id}

    except HTTPException as http_exception:
        raise http_exception

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
