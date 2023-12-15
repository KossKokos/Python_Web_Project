import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

parent_path = Path(__file__).parent.parent.parent
sys.path.append(str(parent_path))

from sqlalchemy.orm import Session

from src.database.models import User
from src.repository.users import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_avatar,
    change_user_role
)
from src.schemas.users import UserModel, UserRoleUpdate


"""To start the test, enter : py test_users.py 
You must be in the killer_instagram/tests/test_repository directory in the console"""


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.attribute_id: str = "id"
        self.new_avatar: str = "new_avatar"
        self.user_db: User = User(
            username='test_username',
            password="test_password",
            email="test@email.com",
            refresh_token="test_refresh_token"
        )
        
    async def test_create_user_ok(self):
        user: UserModel = UserModel(
            username="test_username",
            email="test@email.com",
            password="test_password"
        )
        result = await create_user(body=user, db=self.session)
        self.assertEqual(result.username, user.username)
        self.assertEqual(result.email, user.email)
        self.assertTrue(hasattr(result, self.attribute_id))
        
    async def test_get_user_by_email_ok(self):        
        self.session.query().filter().first.return_value = self.user_db
        result = await get_user_by_email(email=self.user_db.email, db=self.session)
        self.assertEqual(result.username, self.user_db.username)
        self.assertEqual(result.password, self.user_db.password)
        self.assertEqual(result.email, self.user_db.email)
        self.assertTrue(hasattr(result, self.attribute_id))

    async def test_get_user_by_email_none(self):
        email = None
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email=email, db=self.session)
        self.assertIsNone(result)

    async def test_get_user_by_id_ok(self):
        user_id: int = 1
        self.session.query().filter().first.return_value = self.user_db
        result = await get_user_by_id(user_id=user_id, db=self.session)
        self.assertEqual(result.username, self.user_db.username)   
        self.assertEqual(result.password, self.user_db.password)
        self.assertEqual(result.email, self.user_db.email)
        self.assertTrue(hasattr(result, self.attribute_id))

    async def test_get_user_by_id_none(self):
        user_id = None
        self.session.query().filter().first.return_value = None
        result = await get_user_by_id(user_id=user_id, db=self.session)
        self.assertIsNone(result)

    async def test_update_avatar_ok(self):
        self.session.query().filter().first.return_value = self.user_db
        result = await update_avatar(email=self.user_db.email, url=self.new_avatar, db=self.session)
        self.assertEqual(result.avatar, self.new_avatar)

    async def test_update_avatar_none(self):
        self.session.query().filter().first.return_value = None
        with self.assertRaises(AttributeError) as err:
            await update_avatar(email=self.user_db.email, url=self.new_avatar, db=self.session)  

    async def test_change_user_role_ok(self):
        body: UserRoleUpdate = UserRoleUpdate(
            role="admin"
        )
        result = await change_user_role(user=self.user_db, body=body, db=self.session)
        self.assertEqual(result.role, body.role)
        self.assertEqual(result.username, self.user_db.username)
        self.assertTrue(hasattr(result, self.attribute_id))


if __name__ == "__main__":
    unittest.main()