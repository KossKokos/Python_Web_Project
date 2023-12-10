import hashlib

import cloudinary
import cloudinary.uploader

from src.conf.config import settings
from src.database.models import User


class CloudImage:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    @staticmethod
    def generate_name_avatar(email: str):
        user_folder = email
        name = hashlib.sha256(email.encode('utf-8')).hexdigest()[:12]
        return f"User_avatars/{user_folder}{name}"

    @staticmethod
    def generate_name_picture(email: str):
        user_folder = email
        name = hashlib.sha256(email.encode('utf-8')).hexdigest()[:12]
        return f"User_pictures/{user_folder}/{name}"

    @staticmethod
    def upload(file, public_id: str):
        cloud = cloudinary.uploader.upload(
            file,
            public_id=public_id,
            overwrite=True,
            transformation=[
                {"width": 250, "height": 250, "crop": "fill"},
                #  інші трансформації, які потрібні
            ]
        )
        return cloud

    @staticmethod
    def get_url(public_id, cloud):
        src_url = cloudinary.CloudinaryImage(public_id) \
            .build_url(width=250, height=250, crop='fill', version=cloud.get('version'))
        return src_url
    @staticmethod
    def get_transformed_url(original_url: str):
        # Тут можна додати будь-які трансформації URL зображення
        transformed_url = f"{original_url}?width=250&height=250&crop=fill"
        return transformed_url

    @staticmethod
    def download(url: str):
        # Тут представлено лише заглушка
        image_content = b"fake_image_content"
        return BytesIO(image_content)

def generate_qr_code(data: str):
    # Генерація QR-коду з вказаними даними
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Конвертація зображення QR-коду в байти
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
