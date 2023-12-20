import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

parent_path = Path(__file__).parent.parent.parent
sys.path.append(str(parent_path))

from sqlalchemy.orm import Session

from src.database.models import Rating, Image
from src.repository import rating as repository_rating


"""To start the test, enter : py test_rating.py 
You must be in the killer_instagram/tests/test_repository directory in the console"""


class TestRating(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.test_image_id = 1
        self.test_user_id = 1
        self.test_rating = 5
        self.test_rating = Rating(
            id=1,
            rating=self.test_rating,
            image_id=self.test_image_id,
            user_id=self.test_user_id      
        )
        self.test_image_id = 1
        self.test_user_id = 1
        self.test_description = "test_description"
        self.test_image_url = "image_url"
        self.test_public_id = "public_id"
        self.test_tags = ["hello", "world"]
        self.test_file_extension = "jpg"
        self.test_image: Image = Image(
            id=self.test_image_id,
            user_id=self.test_user_id,
            description=self.test_description,
            image_url=self.test_image_url,
            public_id=self.test_public_id,
            file_extension=self.test_file_extension
        )

    async def test_create_rating(self):
        self.session.query().filter().first.return_value = None
        result = await repository_rating.creare_rating(image_id=self.test_image_id, 
                                                       user_id=self.test_user_id,
                                                       rating=self.test_rating,
                                                       db=self.session)
        self.assertIsInstance(result, Rating)
        self.assertTrue(hasattr(result, "id"))
        self.assertEqual(result.image_id, self.test_image_id)
        self.assertEqual(result.user_id, self.test_user_id)

    async def test_create_rating_again(self):
        self.session.query().filter().first.return_value = self.test_rating
        result = await repository_rating.creare_rating(image_id=self.test_image_id, 
                                                       user_id=self.test_user_id,
                                                       rating=self.test_rating,
                                                       db=self.session)
        self.assertFalse(result)

    async def test_get_average_rating_for_image(self):
        average_rating = [5,]
        self.session.query().filter().first.return_value = average_rating
        result = await repository_rating.get_average_rating_for_image(image=self.test_image, db=self.session)
        
        self.assertIsInstance(result, dict)
        self.assertTrue(hasattr(result['image'], "id"))
        self.assertEqual(result['image'].description, self.test_description)
        self.assertEqual(result['rating'], round(average_rating[0], 2))

    async def test_get_average_rating_for_image_not_found(self):
        self.session.query().filter().first.return_value = [None]
        result = await repository_rating.get_average_rating_for_image(image=self.test_image, db=self.session)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
