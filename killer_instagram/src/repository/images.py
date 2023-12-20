import os
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.database.models import Image, Tag, TransformedImageLink, User, image_m2m_tag
from src.repository.tags import get_or_create_tag
from src.schemas.images import ImageModel, ImageResponse, ImageStatusUpdate

from typing import List

async def create_image_with_tags(
    db: Session,
    user: User,
    description: str,
    tags: List[str],
    file_extension: str,
) -> ImageResponse:
    """
    Create an image with tags, upload to Cloudinary, and store in the database.

    Args:
        db (Session): The database session.
        user (User): The user creating the image.
        description (str): The description for the image.
        tags (List[str]): The list of tags for the image.
        file_extension (str): The file extension of the image.

    Returns:
        ImageResponse: The created image.
    """
    image_path = f"images/{user.id}_{description}.{file_extension}"

    image = Image(user_id=user.id, description=description)
    db.add(image)
    db.commit()
    db.refresh(image)


    transformed_link = TransformedImageLink(
        image_id=image.id,
        transformation_url=cloudinary_response["secure_url"],
        qr_code_url=cloudinary_response["qr_code_url"],
    )
    db.add(transformed_link)
    db.commit()

    return ImageResponse.from_orm(image)


async def add_tag_to_image(db: Session, image_id: int, tag_id: int):
    """
    Add a tag to an image in the database.

    Args:
        db (Session): The database session.
        image_id (int): The ID of the image.
        tag_id (int): The ID of the tag.
    """
    db.execute(
        image_m2m_tag.insert().values(image_id=image_id, tag_id=tag_id)
    )
    db.commit()


async def get_image_by_id(db: Session, image_id: int) -> Image | None:
    """
    Get an image by its ID.

    Args:
        db (Session): The database session.
        image_id (int): The ID of the image.

    Returns:
        Image | None: The image or None if not found.
    """
    return db.query(Image).filter(Image.id == image_id).first()


async def get_image_by_id_user_id(image_id: int, user_id: int, db: Session) -> Image | None:
    """
    The get_image_by_id_user_id function returns an image object from the database if it exists.
        Args:
            image_id (int): The id of the image to be retrieved.
            user_id (int): The id of the user who owns this image.
            db (Session, required): SQLAlchemy Session instance.
    
    :param image_id: int: Filter the image by id
    :param user_id: int: Ensure the user is only getting their own images
    :param db: Session: Pass in the database session
    :return: An image object or none
    """
    image = db.query(Image).filter(Image.id==image_id, Image.user_id==user_id).first()
    return image


async def update_image_in_db(db: Session, image_id: int, new_description: str) -> ImageResponse | None:
    """
    Update the description of an image.

    Args:
        db (Session): The database session.
        image_id (int): The ID of the image.
        new_description (str): The new description for the image.

    Returns:
        ImageResponse | None: The updated image or None if not found.
    """
    image = await get_image_by_id(db, image_id)
    if image:
        image.description = new_description
        db.commit()
        db.refresh(image)
        return ImageResponse.from_orm(image)
    return None


async def delete_image_from_db(db: Session, image_id: int) -> bool:
    """
    Delete an image by its ID.

    Args:
        db (Session): The database session.
        image_id (int): The ID of the image.

    Returns:
        bool: True if the image is deleted, False otherwise.
    """
    try:
        # Get the image
        image = db.query(Image).filter(Image.id == image_id).first()

        if image:
            # Delete associated tags
            transformed_links = db.query(TransformedImageLink).filter(TransformedImageLink.image_id==image_id).all()
            for link in transformed_links: # тут добавив видалення transformed links також, бо виникала помилка при видалені фото
                db.delete(link) # вони з'єднані за Foreign key

            db.execute(image_m2m_tag.delete().where(image_m2m_tag.c.image_id == image_id))

            # Delete the image
            db.delete(image)
            return True

        return False
    except Exception as e:
        # Handle exceptions (you might want to log the exception)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting image: {str(e)}",
        )


async def convert_db_model_to_response_model(db: Image) -> ImageResponse:
    """
    Convert a database model (ImageDB) to a response model (ImageResponse).
    """
    response_model = ImageResponse(
        id=db.id,
        user_id=db.user_id,
        description=db.description,
        upload_time=db.upload_time,
    )
    return response_model


async def create_image(
    db: Session,
    user_id: int,
    description: str,
    image_url: str,
    public_id: str,
    tags: List[str],
    file_extension: str,
) -> ImageResponse:
    """
    Create an image and store it in the database.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user creating the image.
        description (str): The description for the image.
        image_url (str): The URL of the image.
        public_id (str): The public ID of the image.
        tags (List[str]): The list of tags for the image.

    Returns:
        ImageResponse: The created image.
    """
    image = Image(
        user_id=user_id,
        description=description,
        image_url=image_url,
        public_id=public_id,
        file_extension=file_extension,
    )
    db.add(image)
    db.commit()
    db.refresh(image)

    for tag_name in tags:
        tag = await get_or_create_tag(db, tag_name="Test")
        await add_tag_to_image(db, image_id=image.id, tag_id=tag.id)

    # return image
    return ImageResponse.from_db_model(image)

async def add_url_public_id(user_id: int, image_id: int, db: Session) -> Image:
    created_image = db.query(Image).filter(Image.user_id==user_id, Image.id==image_id).first()
    return created_image


# async def delete_image_local(
#     db: Session,
#     image: Image
# ) -> ImageResponse:
#     """
#     Delete an image and its corresponding file from the local storage.

#     Args:
#         db (Session): The database session.
#         image (Image): The image to be deleted.

#     Returns:
#         ImageResponse: The deleted image.
#     """

#     # Отримання розширення файлу зображення
#     file_extension = image.file_extension

#     # Фізичне видалення файлу зображення
#     image_path = f"images/{image.user_id}_{image.description}_original.{file_extension}"
#     try:
#         os.remove(image_path)
#     except FileNotFoundError:
#         pass  # Якщо файл вже видалено, ігноруємо помилку

#     return ImageResponse.from_db_model(image)

async def update_image_cloudinary_info(
    db: Session,
    image_id: int,
    image_url: str,
    public_id: str
):
    """
    Updating image information on Cloudinary in the database.

    Args:
        db (Session): Database session.
        image_id (int): ID Image.
        image_url (str): URL Image.
        public_id (str): The public ID of the image on Cloudinary.
    """
    try:
        # Отримання зображення з бази даних
        image = await get_image_by_id(db=db, image_id=image_id)

        # Оновлення URL та public_id в базі даних
        image.image_url = image_url
        image.public_id = public_id

        db.commit()
        db.refresh(image)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating Cloudinary info for image: {str(e)}",
        )

async def get_tags_count_for_image(db: Session, image_id: int) -> int:
    """
    Get the count of tags for an image.

    Args:
        db (Session): The database session.
        image_id (int): The ID of the image.

    Returns:
        int: The count of tags.
    """
    return db.query(image_m2m_tag).filter(image_m2m_tag.c.image_id == image_id).count()


async def check_tags_limit(db: Session, image_id: int) -> bool:
    """
    Check if the number of tags for an image has reached the limit.

    Args:
        db (Session): The database session.
        image_id (int): The ID of the image.

    Returns:
        bool: True if the limit is not reached, False otherwise.
    """
    tags_count = await get_tags_count_for_image(db, image_id)
    return tags_count < 5

async def create_transformed_image_link(
    db: Session,
    image_id: int,
    transformation_url: str,
    qr_code_url: str,
) -> ImageStatusUpdate:
    """
    Create or update a transformed image link and store it in the database.

    Args:
        db (Session): The database session.
        image_id (int): The ID of the original image.
        transformation_url (str): The URL of the transformed image.
        qr_code_url (str): The URL of the QR code for the transformed image.

    Returns:
        ImageStatusUpdate: Status of the operation.
    """
    existing_link = db.query(TransformedImageLink).filter_by(image_id=image_id).first()

    if existing_link:
        # If a record already exists for the given image_id, update it
        existing_link.transformation_url = transformation_url
        existing_link.qr_code_url = qr_code_url
    else:
        # If no record exists, create a new one
        new_link = TransformedImageLink(
            image_id=image_id,
            transformation_url=transformation_url,
            qr_code_url=qr_code_url,
        )
        db.add(new_link)

    db.commit()

    response_data = {
        "done": True,
        "transformation_url": transformation_url,
        "qr_code_url": qr_code_url,
    }

    return ImageStatusUpdate(**response_data)
