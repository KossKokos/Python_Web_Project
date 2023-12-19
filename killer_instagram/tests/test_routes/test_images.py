import sys
from pathlib import Path

path_root = Path(__file__).parent.parent
sys.path.append(str(path_root))

import pytest
from unittest.mock import MagicMock, patch
from jose import jwt 

from src.database.models import User, Image
from src.services.auth import service_auth
from src.conf.config import settings


"""To start the test, enter : pytest tests/test_routes/test_images.py -v 
You must be in the killer_instagram directory in the console"""


"""Fixtures:"""

def test_signup_user(client, session, user, monkeypatch):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        mock_send_email = MagicMock()
        monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
        signup_responce = client.post(
            "/api/auth/signup",
            json=user
        )
        current_user: User = session.query(User).filter(User.email==user["email"]).first()
        current_user.confirmed = True
        session.commit()
        session.refresh(current_user)
        assert signup_responce.status_code == 201, signup_responce.text
        data = signup_responce.json()
        created_user: dict = data["user"]
        assert created_user["email"] == user["email"]
        assert created_user["username"] == user["username"]


def test_get_login_responce(client, user):
    login_responce = client.post(
            "/api/auth/login",
            data={"username": user["email"], "password": user["password"]}
        )
    assert login_responce.status_code == 202, login_responce.text
    login_responce_data = login_responce.json()
    assert login_responce_data["token_type"] == "bearer"


@pytest.fixture(scope="function")
def get_access_token(client, user):
    login_responce = client.post(
            "/api/auth/login",
            data={"username": user["email"], "password": user["password"]}
        )
    data = login_responce.json()
    return data["access_token"]

"""Tests:"""

def test_upload_picture_ok(client, get_access_token, monkeypatch):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        access_token: str = get_access_token

        image_path = r"tests\test_routes\python_logo.jpg"
        file = open(image_path, "rb")

        cloudinary_responce = {"secure_url": "secure_url", "public_id": "public_id"}
        mock_cloud_service = MagicMock(return_value=cloudinary_responce)
        monkeypatch.setattr("src.routes.images.CloudImage.generate_name_image", mock_cloud_service)
        monkeypatch.setattr("src.routes.images.CloudImage.upload_image", mock_cloud_service)
        monkeypatch.setattr("src.routes.images.CloudImage.add_tags", mock_cloud_service)
        
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
        assert image["image_url"] == cloudinary_responce["secure_url"]
        assert image["public_id"] == cloudinary_responce["public_id"]
        assert image["user_id"] == 1

def test_get_image_ok(client):
    image_id = 1
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.get(
            f"api/images/{image_id}",
            headers={"Authorization": f"Bearer {get_access_token}"}
        )
        assert responce.status_code == 200, responce.text
        data = responce.json()
        assert data["id"] == image_id
        assert data["description"] == "test_description"


def test_get_image_not_found(client):
    image_id = 123
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.get(
            f"api/images/{image_id}",
            headers={"Authorization": f"Bearer {get_access_token}"}
        )
        assert responce.status_code == 404, responce.text
        data = responce.json()
        assert data["detail"] == "Image not found"


def test_update_image_description(client, get_access_token, monkeypatch):
    image_id = 1
    new_description = "new_description"
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        mock_cloud_service = MagicMock(return_value=None)
        monkeypatch.setattr("src.routes.images.CloudImage.update_image_description_cloudinary", mock_cloud_service)    
        image_responce = client.put(
            f"api/images/{image_id}?description_update={new_description}",
            headers={"Authorization": f"Bearer {get_access_token}"}            
        )
        assert image_responce.status_code == 202, image_responce.text
        data = image_responce.json()
        assert data["description"] == new_description
        assert data["id"] == image_id

def test_delete_image(client, get_access_token, monkeypatch):
    image_id = 1
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None    
        mock_cloud_service = MagicMock(return_value=None)
        monkeypatch.setattr("src.routes.images.CloudImage.delete_image", mock_cloud_service)
        responce = client.delete(
            f"api/images/{image_id}",
            headers={"Authorization": f"Bearer {get_access_token}"} 
        )
        assert responce.status_code == 202, responce.text
        data = responce.json()
        assert data["message"] == "Image deleted successfully"

def test_delete_image_not_found(client, get_access_token, session, monkeypatch):
    image_id = 1
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None    
        mock_cloud_service = MagicMock(return_value=None)
        monkeypatch.setattr("src.routes.images.CloudImage.delete_image", mock_cloud_service)
        responce = client.delete(
            f"api/images/{image_id}",
            headers={"Authorization": f"Bearer {get_access_token}"} 
        )
        image: None = session.query(Image).filter(Image.id==image_id).first()
        print(image)
        assert responce.status_code == 404, responce.text
        data = responce.json()
        assert data["detail"] == "Image not found"
  