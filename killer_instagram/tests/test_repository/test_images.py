import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

parent_path = Path(__file__).parent.parent.parent
sys.path.append(str(parent_path))

from sqlalchemy.orm import Session

from src.database.models import Image, TransformedImageLink
from src.repository import images as repository_images
from src.schemas import images as schemas_images


"""To start the test, enter : py test_images.py 
You must be in the killer_instagram/tests/test_repository directory in the console"""


class TestImages(unittest.IsolatedAsyncioTestCase):

    
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.test_image_id = 1
        self.test_user_id = 1
        self.test_description = "test_description"
        self.test_image_url = "image_url"
        self.test_public_id = "public_id"
        self.test_tags = ["hello", "world"]
        self.test_file_extension = "jpg"
        self.image: Image = Image(
            id=self.test_image_id,
            user_id=self.test_user_id,
            description=self.test_description,
            image_url=self.test_image_url,
            public_id=self.test_public_id,
            file_extension=self.test_file_extension
        )


    async def test_create_image_ok(self):
        self.session.query().filter().first.return_value = None 
        result: schemas_images.ImageResponse = await repository_images.create_image(
            db=self.session,
            user_id=self.test_user_id,
            description=self.test_description,
            image_url=self.test_image_url,
            public_id=self.test_public_id,
            tags=self.test_tags,
            file_extension=self.test_file_extension
        )
        self.assertEqual(result.description, self.test_description)
        self.assertEqual(result.user_id, self.test_user_id)
        self.assertEqual(result.image_url, self.test_image_url)


    async def test_get_image_by_id_ok(self):
        self.session.query().filter().first.return_value = self.image
        result = await repository_images.get_image_by_id(db=self.session, image_id=self.test_image_id)
        
        self.assertEqual(result.id, self.test_image_id)
        self.assertEqual(result.user_id, self.test_user_id)
        self.assertEqual(result.description, self.test_description)
        self.assertEqual(result.image_url, self.test_image_url)
        self.assertEqual(result.public_id, self.test_public_id)
        self.assertEqual(result.file_extension, self.test_file_extension)


    async def test_get_image_by_id_not_found(self):
        image_id = 99
        self.session.query().filter().first.return_value = None
        result = await repository_images.get_image_by_id(db=self.session, image_id=image_id)
        
        self.assertIsNone(result)


    async def test_update_image_in_db_ok(self):
        new_description = "new_description"
        self.session.query().filter().first.return_value = self.image
        result = await repository_images.update_image_in_db(
            db=self.session, 
            image_id=self.test_image_id, 
            new_description=new_description
        )
        self.assertEqual(result.description, new_description)


    async def test_update_image_in_db_not_found(self):
        new_description = "new_description"
        self.session.query().filter().first.return_value = None
        result = await repository_images.update_image_in_db(
            db=self.session, 
            image_id=self.test_image_id, 
            new_description=new_description
        )
        self.assertIsNone(result)


    async def test_delete_image_from_db_ok(self):
        self.session.query().filter().first.return_value = self.image
        result = await repository_images.delete_image_from_db(db=self.session, image_id=self.test_image_id)
        
        self.assertTrue(result)


    async def test_delete_image_from_db_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await repository_images.delete_image_from_db(db=self.session, image_id=self.test_image_id)
        
        self.assertFalse(result)


    async def test_convert_db_model_to_response_model(self):
        result = await repository_images.convert_db_model_to_response_model(db=self.image)

        self.assertIsInstance(result, schemas_images.ImageResponse)
        self.assertEqual(result.id, self.image.id)
        self.assertEqual(result.description, self.image.description)


    async def test_get_tags_count_for_image(self):
        self.session.query().filter().count.return_value = len(self.test_tags)
        result = await repository_images.get_tags_count_for_image(db=self.session, image_id=self.test_image_id)

        self.assertEqual(result, len(self.test_tags))


    async def test_check_tags_limit_ok(self):
        self.session.query().filter().count.return_value = len(self.test_tags)
        result = await repository_images.check_tags_limit(db=self.session, image_id=self.test_image_id)
        
        self.assertTrue(result)


    async def test_check_tags_limit_more_than_5(self):
        more_than_5_tags = 10
        self.session.query().filter().count.return_value = more_than_5_tags
        result = await repository_images.check_tags_limit(db=self.session, image_id=self.test_image_id)
        
        self.assertFalse(result)


    async def test_create_transformed_image_link(self):
        test_transformation_url = "test_transformation_url"
        test_qr_code_url = "test_qr_code_url"
        self.session.query().filter_by().first.return_value = None
        result = await repository_images.create_transformed_image_link(
            db=self.session,
            image_id=self.test_image_id,
            transformation_url=test_transformation_url,
            qr_code_url=test_qr_code_url
            )
        self.assertIsInstance(result, schemas_images.ImageStatusUpdate)
        self.assertTrue(result.done)


    async def test_find_images_by_keyword(self):
        self.session.query().filter().order_by().all.return_value = [self.image]
        result = await repository_images.find_images_by_keyword(user_id=self.test_user_id,
                                                                db=self.session,
                                                                keyword="test",
                                                                date=True)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0], self.image)


    async def test_find_images_by_tag(self):
        self.session.query().filter().order_by().all.return_value = [self.image]
        result = await repository_images.find_images_by_tag(user_id=self.test_user_id,
                                                                db=self.session,
                                                                tag_name=self.test_tags[0],
                                                                date=True)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0], self.image)        


if __name__ == '__main__':
    unittest.main()