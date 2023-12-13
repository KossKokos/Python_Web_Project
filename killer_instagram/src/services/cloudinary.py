import hashlib

import cloudinary
import cloudinary.uploader
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

from src.conf.config import settings
from src.database.models import User


"""
Тут, клас, який відповідає за з'єднання з cloudinary, треба створити методи для відправлення фото на хмару, форматування,
отримання url і так далі
"""


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
        cloud = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
        return cloud

    @staticmethod
    def get_url(public_id, cloud):
        src_url = cloudinary.CloudinaryImage(public_id) \
            .build_url(width=250, height=250, crop='fill', version=cloud.get('version'))
        return src_url
    

async def upload_to_cloudinary(image_path: str):
    try:
        cloudinary_response = upload(image_path)
        image_url, options = cloudinary_url(cloudinary_response['public_id'], format=cloudinary_response['format'])
        cloudinary_response['image_url'] = image_url
        return cloudinary_response
    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        return None