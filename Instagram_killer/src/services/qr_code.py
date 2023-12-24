import base64
import qrcode
from io import BytesIO

from sqlalchemy.orm import Session
from cloudinary.uploader import upload

from ..database.models import TransformedImageLink
from ..schemas.images import ImageStatusUpdate


async def get_qr_code_url(db: Session, image_id: int) -> str:
    """
    Get the QR code URL for a given image ID from the database.

    Args:
        db (Session): The database session.
        image_id (int): The ID of the image.

    Returns:
        str: The QR code URL or an empty string if not found.
    """
    # Query the TransformedImageLink table for the specified image_id
    qr_code_link = db.query(TransformedImageLink).filter_by(image_id=image_id).first()

    # Return the QR code URL if found, otherwise return an empty string
    return qr_code_link.qr_code_url if qr_code_link else ""

async def save_qr_code_url_to_db(
    db: Session,
    image_id: int,
    transformation_url: str,
    qr_code_url: str,
) -> ImageStatusUpdate:
    """
    Save qr_code link to the database.

    Args:
        db (Session): The database session.
        image_id (int): The ID of the original image.
        transformation_url (str): The URL of the transformed image.
        qr_code_url (str): The URL of the QR code for the transformed image.

    Returns:
        ImageStatusUpdate: Status of the operation.
    """
    try:
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

    except Exception as e:
        db.rollback()
        print(f"Error saving QR code URL to the database: {str(e)}")
        raise


async def generate_qr_code(url: str) -> str:
    """
    Generate QR code for the given data.

    Args:
        url (str): The data to be encoded in the QR code.

    Returns:
        str: The base64-encoded image of the generated QR code.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the QR code as an image file (you can specify a different format if needed)
    buffered = BytesIO()
    img.save(buffered, format="PNG")

    # Get the base64-encoded image
    encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return encoded_image


async def upload_qr_code_to_cloudinary(base64_content: str, public_id: str) -> str:
    """
    Upload the QR code to Cloudinary.

    Args:
        base64_content (str): The base64-encoded content of the QR code image.
        public_id (str): The public ID for the Cloudinary upload.

    Returns:
        str: The public ID of the uploaded QR code.
    """
    # Decode the base64 content
    qr_code_data = base64.b64decode(base64_content)

    # Upload the QR code to Cloudinary
    cloudinary_response = upload(
        file=qr_code_data,
        public_id=public_id,
        overwrite=True,
        format="png",  # Adjust the format as needed
    )

    return cloudinary_response['secure_url']
