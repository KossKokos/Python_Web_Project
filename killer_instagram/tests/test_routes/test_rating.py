import sys
from pathlib import Path

path_root = Path(__file__).parent.parent
sys.path.append(str(path_root))

import pytest
from unittest.mock import MagicMock, patch

from src.database.models import User
from src.services.auth import service_auth



"""To start the test, enter : pytest tests/test_routes/test_rating.py -v 
You must be in the killer_instagram directory in the console"""


"""Global variables:"""
body = {
        "image_id": 1,
        "rating" : 5
    }
body_no_image = {
        "image_id": 102,
        "rating" : 5
    }
rating_id_not_found = 99


"""Fixtures:"""

@pytest.fixture(scope="function")
def signup_admin(client, session, user, monkeypatch):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        mock_send_email = MagicMock()
        monkeypatch.setattr("src.routes.auth.service_email.send_email", mock_send_email)
        signup_responce = client.post(
            "/api/auth/signup",
            json=user
        )
        current_user: User = session.query(User).filter(User.email==user["email"]).first()
        current_user.confirmed = True

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="function")
def signup_user(client, session, user_id_2, monkeypatch):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        mock_send_email = MagicMock()
        monkeypatch.setattr("src.routes.auth.service_email.send_email", mock_send_email)
        signup_responce = client.post(
            "/api/auth/signup",
            json=user_id_2
        )
        current_user: User = session.query(User).filter(User.email==user_id_2["email"]).first()
        current_user.confirmed = True

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="function")
def get_access_token_admin(client, user, signup_admin):
        login_responce = client.post(
            "/api/auth/login",
            data={"username": user["email"], "password": user["password"]}
        )
        data = login_responce.json()
        return data["access_token"]

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="function")
def get_access_token_user(client, user_id_2, signup_user):
        login_responce = client.post(
            "/api/auth/login",
            data={"username": user_id_2["email"], "password": user_id_2["password"]}
        )
        data = login_responce.json()
        return data["access_token"]
#-----------------------------------------------------------------------------------------------------------------------------------------------


"""Tests:"""

def test_upload_image(client, get_access_token_admin, monkeypatch):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        access_token: str = get_access_token_admin

        image_path = r"tests\test_routes\python_logo.jpg"
        file = open(image_path, "rb")

        cloudinary_responce = {"secure_url": "secure_url", "public_id": "public_id"}
        mock_cloud_service = MagicMock(return_value=cloudinary_responce)
        monkeypatch.setattr("src.routes.images.service_cloudinary.CloudImage.generate_name_image", mock_cloud_service)
        monkeypatch.setattr("src.routes.images.service_cloudinary.CloudImage.upload_image", mock_cloud_service)
        monkeypatch.setattr("src.routes.images.service_cloudinary.CloudImage.add_tags", mock_cloud_service)
        
        test_description = "test_description"
        tags = ["hello", "world"]
        image_responce = client.post(
            f"/api/images?description={test_description}&tags={tags}",
            headers={"Authorization": f"Bearer {access_token}"},
            files={"file": ("python_logo.jpg", file, "python_logo.jpg")}
        )
        assert image_responce.status_code == 200, image_responce.text
        data = image_responce.json()
        image: dict = data
        assert image["description"] == test_description

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_rate_image_ok(client, get_access_token_user):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.post(
            "api/images/rating/",
            headers={"Authorization": f"Bearer {get_access_token_user}"},
            json=body
        )
        assert responce.status_code == 200, responce.text
        data = responce.json()
        assert data["id"] == 1
        assert data["image_id"] == body["image_id"]
        assert data["rating"] == body["rating"]

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_rate_image_again(client, get_access_token_user):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.post(
            "api/images/rating/",
            headers={"Authorization": f"Bearer {get_access_token_user}"},
            json=body
        )
        assert responce.status_code == 403, responce.text
        data = responce.json()
        assert data["detail"] == "You have already rated this image before"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_rate_own_image(client, get_access_token_admin):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.post(
            "api/images/rating/",
            headers={"Authorization": f"Bearer {get_access_token_admin}"},
            json=body
        )
        assert responce.status_code == 403, responce.text
        data = responce.json()
        assert data["detail"] == "You can't rate your own image"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_rate_image_not_found(client, get_access_token_user):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.post(
            "api/images/rating/",
            headers={"Authorization": f"Bearer {get_access_token_user}"},
            json=body_no_image
        )
        assert responce.status_code == 404, responce.text
        data = responce.json()
        assert data["detail"] == "Image doesn't exist"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_get_rating_ok(client, get_access_token_admin):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.get(
            f"api/images/rating/{body['image_id']}",
            headers={"Authorization": f"Bearer {get_access_token_admin}"},
        )
        assert responce.status_code == 200, responce.text
        data = responce.json()["Rating"]
        assert data["id"] == 1
        assert data["rating"] == 5

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_get_rating_forbidden(client, get_access_token_user):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.get(
            f"api/images/rating/{body['image_id']}",
            headers={"Authorization": f"Bearer {get_access_token_user}"},
        )
        assert responce.status_code == 403, responce.text
        data = responce.json()
        assert data["detail"] == "Operation forbidden for user"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_get_rating_not_found(client, get_access_token_admin):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.get(
            f"api/images/rating/{rating_id_not_found}",
            headers={"Authorization": f"Bearer {get_access_token_admin}"},
        )
        assert responce.status_code == 404, responce.text
        data = responce.json()
        assert data["detail"] == "Rating doesn't exist"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_get_average_rating_not_found(client, get_access_token_admin, user):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.get(
            f"api/images/{body_no_image['image_id']}/rating",
            headers={"Authorization": f"Bearer {get_access_token_admin}"},
        )
        assert responce.status_code == 404, responce.text
        data = responce.json()
        assert data['detail'] == "Image doesn't exist yet"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_get_average_rating(client, get_access_token_admin, user):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.get(
            f"api/images/{body['image_id']}/rating",
            headers={"Authorization": f"Bearer {get_access_token_admin}"},
        )
        assert responce.status_code == 200, responce.text
        data = responce.json()
        image = data['image']
        rating = data['rating']
        assert image["id"] == body["image_id"]
        assert image['user_id'] == 1
        assert rating == round(body["rating"], 1)

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_delete_rating_no_permission(client, get_access_token_user):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.delete(
            f"api/images/rating/{rating_id_not_found}",
            headers={"Authorization": f"Bearer {get_access_token_user}"},
        )
        assert responce.status_code == 403, responce.text
        data = responce.json()
        assert data["detail"] == "Operation forbidden for user"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_delete_rating_not_found(client, get_access_token_admin):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.delete(
            f"api/images/rating/{rating_id_not_found}",
            headers={"Authorization": f"Bearer {get_access_token_admin}"},
        )
        assert responce.status_code == 404, responce.text
        data = responce.json()
        assert data["detail"] == "Rating not found"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_delete_rating_ok(client, get_access_token_admin):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.delete(
            f"api/images/rating/{body['image_id']}",
            headers={"Authorization": f"Bearer {get_access_token_admin}"},
        )
        assert responce.status_code == 200, responce.text
        data = responce.json()["Deleted raiting"]
        assert data["id"] == 1
        assert data["rating"] == 5
