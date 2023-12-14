import hashlib

import cloudinary
import cloudinary.api
import cloudinary.uploader
from cloudinary.uploader import upload
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
    def generate_name_image(email: str, image_id: int):
        user_folder = email
        name = hashlib.sha256(email.encode('utf-8')).hexdigest()[:12]
        unique_name = f"{image_id}id" + name
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
        # print(f"Updating description on Cloudinary. Public ID: {public_id}, New Description: {new_description}")
        cloudinary.api.update(public_id, context=f"description={new_description}")
        # print("Description updated on Cloudinary.")


    @staticmethod
    def add_tags(public_id: str, tags: List[str]):
        """
        Додавання тегів до зображення на Cloudinary
        """
        tags_str = ','.join(tags)
        cloudinary.api.update(public_id, tags=tags_str, resource_type='image')


    @staticmethod
    def remove_object(image_url, prompt):
        transformation = f"e_gen_remove:prompt_{prompt}"
        return cloudinary.uploader.upload(image_url, transformation=transformation)

    @staticmethod
    def apply_rounded_corners(image_url, width, height):
        transformation = f"c_fill,g_face,w_{width},h_{height}/r_max/f_png"
        return cloudinary.uploader.upload(image_url, transformation=transformation)

    @staticmethod
    def improve_photo(image_url: str):
        width = 100  # Задайте ширину та висоту за потреби
        height = 150
        crop = "fill"
        
        # Отримайте URL та параметри трансформації
        url, options = cloudinary_url(image_url, width=width, height=height, crop=crop)
        
        # Виведіть URL для перевірки
        print(f"Transformed URL: {url}")
        
        # Використовуйте функцію upload з отриманими параметрами
        return cloudinary.uploader.upload(url, **options)


