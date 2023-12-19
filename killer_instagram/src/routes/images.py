from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Query, Body
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.services.auth import service_auth
from src.repository import images as repository_images
from src.repository.images import create_transformed_image_link, get_image_by_id, convert_db_model_to_response_model
from src.schemas.images import ImageModel, ImageResponse, ImageStatusUpdate
from src.database.models import User, TransformedImageLink
from src.database.database import db_transaction
from src.repository.tags import get_existing_tags
from typing import List
from src.services.cloudinary import CloudImage
from src.services.qr_code import get_qr_code_url, generate_qr_code
from src.services.roles import RoleRights
from src.services.logout import logout_dependency

router = APIRouter(prefix='/images', tags=['images'])

allowd_operation_admin= RoleRights(["admin"])
allowd_operation_any_user = RoleRights(["user", "moderator", "admin"])
allowd_operation_delete_user = RoleRights(["admin"])

@router.post("/", 
             status_code=status.HTTP_200_OK,
             dependencies=[Depends(logout_dependency), Depends(allowd_operation_any_user)],
             response_model=ImageResponse)
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
        # for tag_name in tags:
        #     tag = await repository_images.get_or_create_tag(db=db, tag_name=tag_name)
        #     print(73, tag.id)
        #     await repository_images.add_tag_to_image(db=db, image_id=image.id, tag_id=tag.id)

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


@router.delete("/{image_id}",
               dependencies=[Depends(logout_dependency), Depends(allowd_operation_any_user)])
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
        if image.user_id != current_user.id and current_user.role != "admin":
        
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Delete image from /images
        # await repository_images.delete_image_local(db=db, image=image)

        # Delete image from Cloudinary
        CloudImage.delete_image(public_id=image.public_id)

        # Delete image from the database
        await repository_images.delete_image_from_db(db=db, image_id=image_id)

    return {"message": "Image deleted successfully"}


@router.put("/{image_id}",
            dependencies=[Depends(logout_dependency), Depends(allowd_operation_any_user)])
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


@router.get("/{image_id}", response_model=ImageResponse,
            dependencies=[Depends(logout_dependency), Depends(allowd_operation_any_user)])
async def get_image(image_id: int, 
                    db: Session = Depends(get_db),
                    current_user: User = Depends(service_auth.get_current_user)):
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

@router.post("/remove_object/{image_id}",
             dependencies=[Depends(logout_dependency), Depends(allowd_operation_any_user)])
async def remove_object_from_image(
    image_id: int,
    prompt: str,
    db: Session = Depends(get_db),
):
    image = await repository_images.get_image_by_id(db=db, image_id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

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

    # url на  public_id 
    transformed_image = CloudImage.apply_rounded_corners(image.public_id, width, height)
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


@router.post("/get_link_qrcode/{image_id}")
async def get_transformed_image_link_qrcode(
    image_id: int,
    db: Session = Depends(get_db),
):
    """
    Generate a link for the transformed image and QR code.

    Args:
        image_id (int): The ID of the original image.
        db (Session): The database session.

    Returns:
        dict: The response containing the transformation URL and QR code URL.
    """
    # Get image from db
    image = await get_image_by_id(db=db, image_id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Check if a transformed link exists in the database
    transformed_link = await get_transformed_image_link(db=db, image_id=image_id)
    if transformed_link:
        transformation_url = transformed_link.transformation_url
    else:
        # If not found, generate a link for the transformed image
        prompt = "your_prompt_here"  # Replace with your prompt
        transformed_image = CloudImage.remove_object(image.public_id, prompt)
        transformation_url = transformed_image['secure_url']

    # Generate a QR code for the transformation URL
    qr_code_data = generate_qr_code(transformation_url)

    # Save QR code URL to db
    qr_code_url = qr_code_data["url"]
    await create_transformed_image_link(db=db, image_id=image_id, transformation_url=transformation_url, qr_code_url=qr_code_url)

    response_data = {
        "transformation_url": transformation_url,
        "qr_code_url": qr_code_url,
    }

    return response_data