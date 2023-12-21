import sys
from pathlib import Path

path_root = Path(__file__).parent.parent
sys.path.append(str(path_root))

import pytest
from unittest.mock import MagicMock, patch

from src.database.models import User
from src.services.auth import service_auth



"""To start the test, enter : pytest tests/test_routes/test_comments.py -v 
You must be in the killer_instagram directory in the console"""


"""Fixtures:"""

@pytest.fixture(scope="function")
def signup_admin(client, session, user, monkeypatch):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        mock_send_email = MagicMock()
        monkeypatch.setattr("src.routes.auth.service_email.send_email", mock_send_email)
        signup_response = client.post(
            "/api/auth/signup",
            json=user
        )
        current_user: User = session.query(User).filter(User.email==user["email"]).first()
        current_user.confirmed = True
        current_user.role = "admin"

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="function")
def signup_user(client, session, user_id_2, monkeypatch):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        mock_send_email = MagicMock()
        monkeypatch.setattr("src.routes.auth.service_email.send_email", mock_send_email)
        signup_response = client.post(
            "/api/auth/signup",
            json=user_id_2
        )
        current_user: User = session.query(User).filter(User.email==user_id_2["email"]).first()
        current_user.confirmed = True
        current_user.role = 'user'

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="function")
def get_access_token_admin(client, user, signup_admin):
        login_response = client.post(
            "/api/auth/login",
            data={"username": user["email"], "password": user["password"]}
        )
        data = login_response.json()
        return data["access_token"]

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="function")
def get_access_token_user(client, user_id_2, signup_user):
        login_response = client.post(
            "/api/auth/login",
            data={"username": user_id_2["email"], "password": user_id_2["password"]}
        )
        data = login_response.json()
        return data["access_token"]
#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="function")
def upload_image(client, get_access_token_admin, monkeypatch):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        access_token: str = get_access_token_admin

        image_path = r"tests\test_routes\python_logo.jpg"
        file = open(image_path, "rb")

        cloudinary_response = {"secure_url": "secure_url", "public_id": "public_id"}
        mock_cloud_service = MagicMock(return_value=cloudinary_response)
        monkeypatch.setattr("src.routes.images.service_cloudinary.CloudImage.generate_name_image", mock_cloud_service)
        monkeypatch.setattr("src.routes.images.service_cloudinary.CloudImage.upload_image", mock_cloud_service)
        monkeypatch.setattr("src.routes.images.service_cloudinary.CloudImage.add_tags", mock_cloud_service)
        
        test_description = "test_description"
        tags = ["hello", "world"]
        image_response = client.post(
            f"/api/images?description={test_description}&tags={tags}",
            headers={"Authorization": f"Bearer {access_token}"},
            files={"file": ("python_logo.jpg", file, "python_logo.jpg")}
        )
        result = image_response.json()
        return result


"""Tests:"""

def test_write_comment_ok(client, get_access_token_user, upload_image):
     with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        comment = {
             "comment": "test comment",
             "image_id": upload_image["id"]
        }
        response = client.post(
             "api/images/comments/",
             headers={"Authorization": f"Bearer {get_access_token_user}"},
             json=comment
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['comment'] == comment['comment']

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_write_comment_image_not_found(client, get_access_token_user):
     with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        comment = {
             "comment": "test comment",
             "image_id": 100
        }
        response = client.post(
             "api/images/comments/",
             headers={"Authorization": f"Bearer {get_access_token_user}"},
             json=comment
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data['detail'] == "Image doesn't exist"
        
#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_write_comment_for_own_image(client, get_access_token_admin, upload_image):
     with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        comment = {
             "comment": "test comment",
             "image_id": upload_image['id']
        }
        response = client.post(
             "api/images/comments/",
             headers={"Authorization": f"Bearer {get_access_token_admin}"},
             json=comment
        )
        assert response.status_code == 403, response.text
        data = response.json()
        assert data['detail'] == "You can't comment your own image"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_get_comment_ok(client, get_access_token_admin, upload_image):
     with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        comment = {
             "comment": "test comment",
             "image_id": upload_image['id']
        }
        response = client.get(
             f"api/images/comments/{1}",
             headers={"Authorization": f"Bearer {get_access_token_admin}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['comment'] == comment["comment"]
        assert data['image_id'] == 1

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_get_comment_not_found(client, get_access_token_admin):
     with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        not_exist_comment_id = 100
        response = client.get(
             f"api/images/comments/{not_exist_comment_id}",
             headers={"Authorization": f"Bearer {get_access_token_admin}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data['detail'] == "Comment doesn't exist"

#-----------------------------------------------------------------------------------------------------------------------------------------------
    
def test_update_comment_ok(client, get_access_token_user):
     with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        updated_comment = {
             "new_comment": "test new_comment"
        }
        response = client.put(
             f"api/images/comments/{1}",
             headers={"Authorization": f"Bearer {get_access_token_user}"},
             json=updated_comment
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['comment'] == updated_comment["new_comment"]
        assert data['image_id'] == 1

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_update_comment_not_found(client, get_access_token_user):
     with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        updated_comment = {
             "new_comment": "test new_comment"
        }
        not_exist_comment_id = 100
        response = client.put(
             f"api/images/comments/{not_exist_comment_id}",
             headers={"Authorization": f"Bearer {get_access_token_user}"},
             json=updated_comment
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data['detail'] == "Comment not found"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_delete_comment_forbidden(client, get_access_token_user):
     with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
             f"api/images/comments/{1}",
             headers={"Authorization": f"Bearer {get_access_token_user}"},
        )
        assert response.status_code == 403, response.text
        data = response.json()
        comment = data["detail"] == "Operation forbidden for user"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_delete_comment_ok(client, get_access_token_admin):
     with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
             f"api/images/comments/{1}",
             headers={"Authorization": f"Bearer {get_access_token_admin}"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        comment = data["Deleted comment"]
        assert comment["id"] == 1
        assert comment["image_id"] == 1



