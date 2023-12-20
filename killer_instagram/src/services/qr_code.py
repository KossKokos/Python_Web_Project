import base64
import qrcode
from io import BytesIO
from sqlalchemy.orm import Session
from src.database.models import TransformedImageLink
from src.services.cloudinary import CloudImage

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

def generate_qr_code(url: str) -> dict:
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
    # with open("qrcode.png", "rb") as image_file:
    #     encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    return encoded_image

def generate_and_upload_qr_code(url: str, public_id: str) -> dict:
    """
    Generate a QR code for the given URL and upload it to Cloudinary.

    Args:
        url (str): The URL for the QR code.
        public_id (str): The public ID for the QR code in Cloudinary.

    Returns:
        dict: Cloudinary response for the uploaded QR code.
    """
    qr_code_data = generate_qr_code(url)
    
    # Upload the QR code to Cloudinary
    qr_code_upload_response = CloudImage.upload_image(
        qr_code_data,
        public_id=public_id,
        overwrite=True,
    )
    
    return qr_code_upload_response

