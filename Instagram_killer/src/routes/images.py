from typing import List, Optional

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.database.db import get_db, db_transaction
from src.schemas import images as schemas_images
from src.database.models import User, Image
from src.services.auth import service_auth
from src.services import (
    roles as service_roles,
    logout as service_logout,
    banned as service_banned,
    qr_code as service_qr_code,
    cloudinary as service_cloudinary
)
from src.repository import (
    images as repository_images, 
    rating as repository_rating, 
    tags as repository_tags
)

router = APIRouter(prefix='/images', tags=['images'])


allowd_operation_admin= service_roles.RoleRights(["admin"])
allowd_operation_any_user = service_roles.RoleRights(["user", "moderator", "admin"])
allowd_operation_delete_user = service_roles.RoleRights(["admin"])

@router.post("/", 
             status_code=status.HTTP_200_OK,
             dependencies=[Depends(service_logout.logout_dependency), 
                           Depends(allowd_operation_any_user),
                           Depends(service_banned.banned_dependency)],
             response_model=schemas_images.ImageResponse)
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
        public_id = service_cloudinary.CloudImage.generate_name_image(email=current_user.email, filename=file.filename)
        cloudinary_response = service_cloudinary.CloudImage.upload_image(file=file.file, public_id=public_id)

        # Save image information to the database
        image: Image = await repository_images.create_image(
            db=db,
            user_id=current_user.id,
            description=description,
            image_url=cloudinary_response["secure_url"],
            public_id=cloudinary_response["public_id"],
            tags=tags,
            file_extension=file_extension,
        )

        # Add new tags to the existing tags list
        existing_tags = await repository_tags.get_existing_tags(db)
        for tag_name in tags:
            if tag_name not in existing_tags:
                existing_tags.append(tag_name)

        # Add tags to the uploaded image on Cloudinary
        service_cloudinary.CloudImage.add_tags(cloudinary_response["public_id"], tags)

        return image
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}",
        )


@router.delete("/{image_id}",
               dependencies=[Depends(service_logout.logout_dependency), 
                             Depends(allowd_operation_any_user),
                             Depends(service_banned.banned_dependency)], 
                             status_code=status.HTTP_202_ACCEPTED)
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

        # Delete image from Cloudinary
        service_cloudinary.CloudImage.delete_image(public_id=image.public_id)

        # Delete image from the database
        await repository_images.delete_image_from_db(db=db, image_id=image_id)

    return {"message": "Image deleted successfully"}


@router.put("/{image_id}",
            dependencies=[Depends(service_logout.logout_dependency), 
                          Depends(allowd_operation_any_user),
                          Depends(service_banned.banned_dependency)])
async def update_image_description(
    image_id: int,
    body: schemas_images.ImageDescriptionUpdate,
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
        image = await repository_images.update_image_in_db(db=db, image_id=image_id, new_description=body.new_description)

        # Asynchronously update image information on Cloudinary
        service_cloudinary.CloudImage.update_image_description_cloudinary(image.public_id, body.new_description)

        return image
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}",
        )


@router.get("/{image_id}", response_model=schemas_images.ImageResponse,
            dependencies=[Depends(service_logout.logout_dependency), 
                          Depends(allowd_operation_any_user),
                          Depends(service_banned.banned_dependency)], 
                          status_code=status.HTTP_200_OK)
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
    image_response = schemas_images.ImageResponse.from_db_model(image)

    return image_response


@router.get("/transformed_image/{image_id}", response_model=schemas_images.ImageResponse)
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
    
    image_response = schemas_images.ImageResponse.from_db_model(image)

    # Отримати трансформовані посилання для цього зображення
    links = image_response.transformed_links

    return schemas_images.ImageResponse(
        id=image_response.id,
        user_id=image_response.user_id,
        public_id=image_response.public_id,
        description=image_response.description,
        transformed_links=links,
        image_url=image_response.image_url,
    )


@router.patch("/remove_object/{image_id}",
             dependencies=[Depends(service_logout.logout_dependency), 
                           Depends(allowd_operation_any_user),
                           Depends(service_banned.banned_dependency)], 
                           status_code=status.HTTP_202_ACCEPTED)
async def remove_object_from_image(
    image_id: int,
    prompt: str = "Star",
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
    """
    The remove_object_from_image function removes an object from the image.
    
    :param image_id: int: Fetch the image from the database
    :param prompt: str: Specify the object to be removed from the image
    :param current_user: User: Get the current user information
    :param db: Session: Access the database
    :param : Specify the object to be removed from the image
    :return: ImageStatusUpdate model
    """
    # Fetch the original image URL from the database
    image = await repository_images.get_image_by_id(db=db, image_id=image_id)

    # Check if the current user has permission to update the image
    if image.user_id != current_user.id and current_user.role != "admin":
                raise HTTPException(status_code=403, detail="Permission denied")

    #image = await repository_images.get_image_by_id(db=db, image_id=image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        transformed_image = service_cloudinary.CloudImage.remove_object(image.public_id, prompt)
        transformation_url = transformed_image['secure_url']

        # Check if QR code URL exists in the database
        qr_code_link = await service_qr_code.get_qr_code_url(db=db, image_id=image.id)

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

        return schemas_images.ImageStatusUpdate(**response_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}",
        )


@router.post("/apply_rounded_corners/{image_id}",
             dependencies=[Depends(service_logout.logout_dependency), 
                           Depends(allowd_operation_any_user),
                           Depends(service_banned.banned_dependency)])
async def apply_rounded_corners_to_image(
    image_id: int,
    border: str = "5px_solid_black",
    radius: int = 50,
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
    """
    The apply_rounded_corners_to_image function applies rounded corners to an image.
    
    :param image_id: int: Get the image from the database
    :param border: str: Specify the border color and thickness of the rounded corners
    :param radius: int: Set the radius of the rounded corners
    :param current_user: User: Check if the current user has permission to update the image
    :param db: Session: Pass the database session to the function
    :return: A json response like this:
    """
    image = await repository_images.get_image_by_id(db=db, image_id=image_id)

    # Check if the current user has permission to update the image
    if image.user_id != current_user.id and current_user.role != "admin":
                raise HTTPException(status_code=403, detail="Permission denied")

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        transformed_image = service_cloudinary.CloudImage.apply_rounded_corners(image.public_id, border, radius)
        transformation_url = transformed_image['secure_url']

        # Check if QR code URL exists in the database
        qr_code_link = await service_qr_code.get_qr_code_url(db=db, image_id=image.id)

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

        return schemas_images.ImageStatusUpdate(**response_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}",
        )


@router.put("/improve_photo/{image_id}",
            dependencies=[Depends(service_logout.logout_dependency), 
                          Depends(allowd_operation_any_user),
                          Depends(service_banned.banned_dependency)])
async def improve_photo(
    image_id: int,
    mode: str = 'outdoot',
    blend: int = 100,
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db),
):
    """
    The improve_photo function takes an image_id, mode and blend as input.
    It then checks if the current user has permission to update the image. If not, it raises a 403 error.
    If there is no such image in the database, it raises a 404 error. 
    Otherwise, it calls Cloudinary's improve_photo function with mode and blend parameters to transform the original photo into an improved one (e.g., outdoor or indoor). 
    The transformed photo is saved in Cloudinary's cloud storage and its URL is returned back to us.
    
    :param image_id: int: Identify the image to be transformed
    :param mode: str: Determine the type of transformation to be applied
    :param blend: int: Specify the blending level of the image
    :param current_user: User: Get the current user's information
    :param db: Session: Pass the database session to the function
    :param : Specify the mode of transformation
    :return: json
    """
    image = await repository_images.get_image_by_id(db=db, image_id=image_id)

    # Check if the current user has permission to update the image
    if image.user_id != current_user.id and current_user.role != "admin":
                raise HTTPException(status_code=403, detail="Permission denied")

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
  
    try:
        transformed_image = service_cloudinary.CloudImage.improve_photo(image.image_url, mode, blend)
        transformation_url = transformed_image['secure_url']

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


@router.get("/get_link_qrcode/{image_id}",
            dependencies=[Depends(service_logout.logout_dependency), 
                          Depends(allowd_operation_any_user),
                          Depends(service_banned.banned_dependency)])
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

        image_response = schemas_images.ImageResponse.from_db_model(image)

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

        image_response = schemas_images.ImageResponse.from_db_model(image)

        # Перевірити, чи список не порожній
        if not image_response.transformed_links:
            raise HTTPException(status_code=404, detail="No transformed links found for the image")

        # Отримати перший URL трансформованого зображення
        selected_transformation_url = image_response.transformed_links[0].transformation_url if image_response.transformed_links else None

        # Генерація QR-коду
        qr_code = await service_qr_code.generate_qr_code(selected_transformation_url)

        publick_id = service_cloudinary.CloudImage.generate_name_image(email=current_user.email, filename="qr_code")

        # Оновити Cloudinary і зберегти QR-код
        qr_code_publick_id = await service_qr_code.upload_qr_code_to_cloudinary(qr_code, public_id=publick_id)

        # Оновити посилання на QR-код в базі даних
        await service_qr_code.save_qr_code_url_to_db(
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



@router.get("/{image_id}/rating", status_code=200,
            dependencies=[Depends(service_logout.logout_dependency), Depends(allowd_operation_any_user)])
async def get_average_rating(image_id: int, 
                     current_user: User = Depends(service_auth.get_current_user),
                     db: Session = Depends(get_db)):
    """
    The get_rating function returns the average rating for a given image.
        The function takes an image_id as input and returns the average rating of that image.
        If no ratings have been made yet, it will return a message saying so.
    
    :param image_id: int: Get the image id from the request
    :param current_user: User: Get the user that is currently logged in
    :param db: Session: Get the database session
    :return: A dictionary with the message key
    """
    image: Image = await repository_images.get_image_by_id(db=db, image_id=image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="Image doesn't exist yet")
    average_rating = await repository_rating.get_average_rating_for_image(image=image, db=db)
    if average_rating is None:
        return HTTPException(status_code=404, detail="Image has no rating yet")
    return average_rating


@router.get('/find/by_keyword', status_code=200)
async def find_images_by_keyword(keyword: str, 
                      date: Optional[bool] = False,
                      current_user: User = Depends(service_auth.get_current_user),
                      db: Session = Depends(get_db)):
    """
    The find_images_by_keyword function finds images by keyword.
        Args:
            keyword (str): The search term to find images by.
            date (bool, optional): Whether or not to sort the results by date. Defaults to False.
            current_user (User): a user who is currently making a request

    :param keyword: str: Search for images by keyword
    :param date: Optional[bool]: Determine whether the images should be sorted by date or not
    :param current_user: User: Get the user id of the current logged in user
    :param db: Session: Pass the database session to the repository layer
    :return: A list of images
    """
    images = await repository_images.find_images_by_keyword(keyword=keyword, 
                                                date=date, 
                                                user_id=current_user.id, db=db)
    return images
    

@router.get('/find/by_tag', status_code=200)
async def find_images_by_tag(tag: str, 
                      date: Optional[bool] = False,
                      current_user: User = Depends(service_auth.get_current_user),
                      db: Session = Depends(get_db)):
    """
    The find_images_by_tag function returns a list of images that have the specified tag.
        The user must be logged in to use this function.
        If no images are found, an HTTPException is raised with status code 404 and detail message
    
    :param tag: str: Get the tag name from the request
    :param date: Optional[bool]: Determine if the user wants to sort by date or not
    :param current_user: User: Get the user_id of the current user
    :param db: Session: Get the database session, which is used to query the database
    :return: A list of images
    """
    images = await repository_images.find_images_by_tag(tag_name=tag, 
                                                date=date, 
                                                user_id=current_user.id, db=db)
    if images is None:
        raise HTTPException(status_code=404, detail="There are no images with this tag")
    return images