import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

parent_path = Path(__file__).parent.parent.parent
sys.path.append(str(parent_path))

from sqlalchemy.orm import Session

from src.repository.logout import token_to_blacklist, is_token_blacklisted


"""To start the test, enter : py test_logout.py 
You must be in the killer_instagram/tests/test_repository directory in the console"""


class TestLogout(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.token = "access_token"
        self.user_id = 1

    async def test_token_to_blacklist_ok(self):
        self.session.query().filter().first.return_value = None
        result = await token_to_blacklist(access_token=self.token, user_id=self.user_id , db=self.session)
        self.assertEqual(result.blacklisted_token, self.token)
        self.assertTrue(hasattr(result, "id"))

    async def test_is_token_blacklisted_true(self):
        self.session.query().filter().first.return_value = self.token
        result = await is_token_blacklisted(user_id=self.user_id, db=self.session)
        self.assertEqual(result, "Old blacklist_token removed")

    async def test_is_token_blacklisted_false(self):
        self.session.query().filter().first.return_value = None
        result = await is_token_blacklisted(user_id=self.user_id, db=self.session)
        self.assertEqual(result, "Ready to write a new blacklist_token")


if __name__ == '__main__':
    unittest.main()