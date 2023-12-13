from sqlalchemy.orm import Session
from src.database.models import Image, Tag, TransformedImageLink, User, image_m2m_tag
from src.repository.tags import get_or_create_tag
from src.schemas.images import ImageModel, ImageResponse
from src.services.cloudinary import upload_to_cloudinary

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

    cloudinary_response = upload_to_cloudinary(image_path)

    image_url = cloudinary_response["secure_url"]
    image.public_id = cloudinary_response["public_id"]
    db.commit()

    for tag_name in tags:
        tag = get_or_create_tag(db, tag_name)
        db.execute(
            image_m2m_tag.insert().values(image_id=image.id, tag_id=tag.id)
        )

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


async def update_image_description(db: Session, image_id: int, new_description: str) -> ImageResponse | None:
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


async def delete_image(db: Session, image_id: int) -> bool:
    """
    Delete an image by its ID.

    Args:
        db (Session): The database session.
        image_id (int): The ID of the image.

    Returns:
        bool: True if the image is deleted, False otherwise.
    """
    try:
        # Start a transaction
        with db.begin():
            image = db.query(Image).filter(Image.id == image_id).first()

            if image:
                # Delete associated tags
                db.execute(image_m2m_tag.delete().where(image_m2m_tag.c.image_id == image_id))

                # Delete the image
                db.delete(image)
                return True

        return False
    except Exception as e:
        # Handle exceptions and rollback the transaction
        db.rollback()
        raise e

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
    # TODO Зміна назви зображення на сервері Cloudinary
    # public_id = f"{user_id}_{description}"

    image = Image(
        user_id=user_id,
        description=description,
        image_url=image_url,
        public_id=public_id,
    )
    db.add(image)
    db.commit()
    db.refresh(image)

    for tag_name in tags:
        tag = await get_or_create_tag(db, tag_name="Test")
        await add_tag_to_image(db, image_id=image.id, tag_id=tag.id)

    return ImageResponse.from_orm(image)

