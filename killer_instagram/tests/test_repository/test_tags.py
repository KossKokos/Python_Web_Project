import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

parent_path = Path(__file__).parent.parent.parent
sys.path.append(str(parent_path))

from sqlalchemy.orm import Session

from src.database.models import Tag
from src.repository import tags as repository_tags


"""To start the test, enter : py test_tags.py 
You must be in the killer_instagram/tests/test_repository directory in the console"""


class TestTags(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.test_tag_name = "test_tag_name"
        self.test_tag: Tag = Tag(
            id=1,
            tag=self.test_tag_name
        )
        self.empty_list = []

    async def test_get_or_create_tag_create(self):
        self.session.query().filter().first.return_value = None
        result = await repository_tags.get_or_create_tag(db=self.session, tag_name=self.test_tag_name)

        self.assertIsInstance(result, Tag)
        self.assertEqual(result.tag, self.test_tag_name)

    async def test_get_or_create_tag_get(self):
        self.session.query().filter().first.return_value = self.test_tag
        result = await repository_tags.get_or_create_tag(db=self.session, tag_name=self.test_tag_name)

        self.assertIsInstance(result, Tag)
        self.assertEqual(result.id, self.test_tag.id)
        self.assertEqual(result.tag, self.test_tag.tag)

    async def test_get_existing_tags(self):
        self.session.query().distinct().all.return_value = [self.test_tag]
        result = await repository_tags.get_existing_tags(db=self.session)

        self.assertIsInstance(result, list)
        self.assertEqual(result[0], self.test_tag_name)

    async def test_get_existing_tags_none(self):
        self.session.query().distinct().all.return_value = self.empty_list
        result = await repository_tags.get_existing_tags(db=self.session)

        self.assertIsInstance(result, list)
        self.assertEqual(result, self.empty_list)
    
    
if __name__ == '__main__':
    unittest.main()