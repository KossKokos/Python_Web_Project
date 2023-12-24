import hashlib
from typing import List

import cloudinary
from cloudinary import api
from cloudinary.api import update
from cloudinary import CloudinaryImage
from cloudinary import uploader
from cloudinary.utils import cloudinary_url

from ..conf.config import settings


class CloudImage:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    @staticmethod
    def generate_name_avatar(email: str):
        """
        The generate_name_avatar function takes an email address as a string and returns the path to where the avatar should be stored.
        The function uses SHA256 hashing to generate a unique name for each user's avatar, which is then appended to their folder.
        
        :param email: str: Specify the type of data that is expected to be passed into the function
        :return: The path of the avatar
        """
        user_folder = email
        name = hashlib.sha256(email.encode('utf-8')).hexdigest()[:12]
        return f"Users/{user_folder}/Avatar/{name}"

    @staticmethod
    def generate_name_image(email: str, filename: int):
        """
        The generate_name_image function takes in an email and a filename,
            hashes the email to create a unique name for the image, then returns
            that name with the filename as well. This is used to ensure that no two images have 
            identical names.
        
        :param email: str: Pass in the email address of the user
        :param filename: int: Make sure that the image has a unique name
        :return: A string, so you can use it in the upload_file function like this:
        """
        user_folder = email
        name = hashlib.sha256(email.encode('utf-8')).hexdigest()[:12]
        unique_name = f"{filename}," + name
        return f"Users/{user_folder}/Images/{unique_name}"

    @staticmethod
    def upload_avatar(file, public_id: str):
        """
        The upload_avatar function uploads an avatar to Cloudinary.
            Args:
                file (str): The path of the image file to be uploaded.
                public_id (str): The public ID of the image on Cloudinary.
        
        :param file: Upload the file to cloudinary
        :param public_id: str: Specify the public id of the image to be uploaded
        :return: A dictionary 
        """
        cloud = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
        return cloud

    @staticmethod
    def upload_image(file, public_id: str):
        """
        The upload_image function takes a file and public_id as arguments.
        The function then uploads the file to Cloudinary using the public_id provided.
        If an image with that public_id already exists, it will not be overwritten.
        
        :param file: Upload the image to cloudinary
        :param public_id: str: Set the public_id of the image
        :return: A dictionary
        """
        cloud = cloudinary.uploader.upload(file, public_id=public_id, overwrite=False)
        return cloud

    @staticmethod
    def get_url(public_id, cloud):
        """
        The get_url function takes a public_id and cloud object as arguments.
            It then uses the CloudinaryImage class to build a URL for an image with the given public_id,
            using the width, height, crop and version parameters from the cloud object.
        
        
        :param public_id: Specify the image that is to be displayed
        :param cloud: Get the version number of the image
        :return: The url of the image
        """
        src_url = cloudinary.CloudinaryImage(public_id) \
            .build_url(width=250, height=250, crop='fill', version=cloud.get('version'))
        return src_url

    @staticmethod
    def delete_image(public_id: str):
        """
        The delete_image function deletes an image from the cloudinary server.
            Args:
                public_id (str): The unique identifier of the image to be deleted.
        
        
        :param public_id: str: Specify the public id of the image to be deleted
        :return: A dictionary 
        """
        cloudinary.uploader.destroy(public_id)

    @staticmethod
    def update_image_description_cloudinary(public_id: str, new_description: str):
        """
        The update_image_description_cloudinary function updates the description of an image in Cloudinary.
            Args:
                public_id (str): The public ID of the image to update.
                new_description (str): The new description for the image.
        
        :param public_id: str: Identify the image in cloudinary
        :param new_description: str: Pass in the new description that you want to set for the image
        :return: A dictionary
        """
        cloudinary.api.update(public_id, context=f"description={new_description}")

    @staticmethod
    def add_tags(public_id: str, tags: List[str]):
        """
        The add_tags function takes a public_id and a list of tags as arguments.
        It then converts the list of tags into a comma-separated string, which is 
        the format that Cloudinary expects for its API calls. It then uses the 
        Cloudinary API to update the image with those tags.
        
        :param public_id: str: Identify the image in cloudinary
        :param tags: List[str]: Specify the type of data that is expected to be passed into the function
        :return: A dictionary of the image's updated metadata
        """
        tags_str = ','.join(tags)
        cloudinary.api.update(public_id, tags=tags_str, resource_type='image')

    @staticmethod
    def remove_object(public_id, prompt):
        """
        The remove_object function takes a public_id and prompt as arguments.
        The function then uses the cloudinary_url function to generate a URL for the image with the gen_remove effect applied, 
        and uploads that transformed image to Cloudinary. The public id of this new object is returned.
        
        :param public_id: Identify the image to be transformed
        :param prompt: Specify the prompt that is to be removed from the image
        :return: A dictionary 
        """
        transformed_image_url = cloudinary_url(public_id, effect=f"gen_remove:prompt_{prompt}", secure=True)[0]
        return cloudinary.uploader.upload(transformed_image_url)
        # transformation = f"e_gen_remove:prompt_{prompt}"
        # return cloudinary.api.update(public_id, transformation=transformation)

    @staticmethod
    def apply_rounded_corners(public_id, border, radius):
        """
        The apply_rounded_corners function takes a public_id, border and radius as arguments.
        It then uses the cloudinary_url function to generate a URL for the image with rounded corners.
        The transformed image is then uploaded to Cloudinary using uploader.upload.
        
        :param public_id: Specify the image that you want to apply rounded corners to
        :param border: Add a border around the image
        :param radius: Round the corners of an image
        :return: A dictionary 
        """
        transformed_image_url = cloudinary_url(public_id, transformation=[{'border': border, 'radius': radius}], secure=True)[0]
        return cloudinary.uploader.upload(transformed_image_url)

    @staticmethod
    def improve_photo(public_id, mode, blend):
        """
        The improve_photo function takes a public_id, mode, and blend as arguments.
        It then uses the cloudinary_url function to generate a URL for the image with 
        the given transformation parameters. It then uploads that transformed image to 
        Cloudinary and returns its new public ID.
        
        :param public_id: Identify the image to be transformed
        :param mode: Specify the type of image processing to be applied
        :param blend: Blend the image with a color
        :return: A dictionary 
        """
        transformed_image_url = cloudinary_url(public_id, transformation=[{'mode': mode, 'blend': blend}], secure=True)[0]
        return cloudinary.uploader.upload(transformed_image_url)
