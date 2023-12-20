import hashlib

import cloudinary
from cloudinary import api
from cloudinary.api import resource, update
from cloudinary import CloudinaryImage
from cloudinary import uploader
from cloudinary.utils import cloudinary_url
from typing import List

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
        return f"Users/{user_folder}/Avatar/{name}"

    @staticmethod
    def generate_name_image(email: str, filename: int):
        user_folder = email
        name = hashlib.sha256(email.encode('utf-8')).hexdigest()[:12]
        # тут замінив image_id на filename, так як можна створювати унікальне ім'я за цим, монжна поміняти на будь-що
        unique_name = f"{filename}," + name
        return f"Users/{user_folder}/Images/{unique_name}"

    @staticmethod
    def upload_avatar(file, public_id: str):
        cloud = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
        return cloud

    @staticmethod
    def upload_image(file, public_id: str):
        cloud = cloudinary.uploader.upload(file, public_id=public_id, overwrite=False)
        return cloud

    @staticmethod
    def get_url(public_id, cloud):
        src_url = cloudinary.CloudinaryImage(public_id) \
            .build_url(width=250, height=250, crop='fill', version=cloud.get('version'))
        return src_url

    @staticmethod
    def delete_image(public_id: str):
        """
        Видалення зображення за його public_id
        """
        cloudinary.uploader.destroy(public_id)

    @staticmethod
    def update_image_description_cloudinary(public_id: str, new_description: str):
        """
        Оновлення опису зображення на Cloudinary.
        """
        cloudinary.api.update(public_id, context=f"description={new_description}")

    @staticmethod
    def add_tags(public_id: str, tags: List[str]):
        """
        Додавання тегів до зображення на Cloudinary
        """
        tags_str = ','.join(tags)
        cloudinary.api.update(public_id, tags=tags_str, resource_type='image')

    @staticmethod
    def remove_object(public_id, mode, prompt):
        # e_gen_remove:prompt_Star
        transformed_image_url = cloudinary_url(public_id, effect=f"gen_remove:prompt_{prompt}", secure=True)[0]
        return cloudinary.uploader.upload(transformed_image_url)

    @staticmethod
    def apply_rounded_corners(public_id, border, radius):
        transformed_image_url = cloudinary_url(public_id, transformation=[{'border': border, 'radius': radius}], secure=True)[0]
        print(f"Transformed @staticmethod URL: {transformed_image_url}")
        return cloudinary.uploader.upload(transformed_image_url)

    @staticmethod
    def improve_photo(public_id, mode, blend):
        transformed_image_url = cloudinary_url(public_id, transformation=[{'mode': mode, 'blend': blend}], secure=True)[0]
        print(f"Transformed @staticmethod URL: {transformed_image_url}")
        return cloudinary.uploader.upload(transformed_image_url)
