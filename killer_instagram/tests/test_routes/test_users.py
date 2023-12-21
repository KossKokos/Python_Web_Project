import sys
from pathlib import Path

path_root = Path(__file__).parent.parent
sys.path.append(str(path_root))

import pytest
from unittest.mock import MagicMock, patch

from src.database.models import User
from src.services.auth import service_auth


"""To run tests, enter: pytest tests/test_routes/test_users.py -v
in the killer_instagram directory in the console"""

#-----------------------------------------------------------------------------------------------------------------------------------------------
"""Fixtures:"""

@pytest.fixture(scope="function")
def access_token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.service_email.send_email", mock_send_email)
    signup_response = client.post(
        "/api/auth/signup",
        json=user,
    )
    created_user: User = session.query(User).filter(User.email==user["email"]).first()
    created_user.confirmed = True
    session.commit()
    session.refresh(created_user)
    login_response = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    data = login_response.json()
    access_token = data["access_token"]
    return access_token

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="function")
def no_email_token():
    data = {"sub": "wrong_email"}
    token = service_auth.sync_create_access_token(data=data)
    return token

#-----------------------------------------------------------------------------------------------------------------------------------------------
"""Tests:"""

def test_read_users_me_ok(client, access_token, user):
     with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {access_token}"}
        ) 
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["username"] == user["username"]
        assert data["email"] == user["email"]
        assert "id" in data

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_read_users_me_no_user(client, no_email_token):
     with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {no_email_token}"}
        ) 
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == "Could not validate credentials"
        
#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_update_avatar_no_user(client, no_email_token, monkeypatch):
    mock_cloud_service = MagicMock(return_value="image_url")
    monkeypatch.setattr("src.routes.users.service_cloudinary.CloudImage.generate_name_avatar", mock_cloud_service)
    monkeypatch.setattr("src.routes.users.service_cloudinary.CloudImage.upload_avatar", mock_cloud_service)
    monkeypatch.setattr("src.routes.users.service_cloudinary.CloudImage.get_url", mock_cloud_service)
    image_path = r"tests\test_routes\python_logo.jpg"
    file = open(image_path, "rb")
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.patch(
        "api/users/avatar",
        files={"file": ("filename", file, "python_logo.jpg")},
        headers={"Authorization": f"Bearer {no_email_token}"}
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Could not validate credentials"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_update_avatar_ok(client, access_token, monkeypatch):
    new_avatar = "image_url"
    mock_cloud_service = MagicMock(return_value=new_avatar)
    monkeypatch.setattr("src.routes.users.service_cloudinary.CloudImage.generate_name_avatar", mock_cloud_service)
    monkeypatch.setattr("src.routes.users.service_cloudinary.CloudImage.upload_avatar", mock_cloud_service)
    monkeypatch.setattr("src.routes.users.service_cloudinary.CloudImage.get_url", mock_cloud_service)
    image_path = r"tests\test_routes\python_logo.jpg"
    file = open(image_path, "rb")
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.patch(
        "api/users/avatar",
        files={"file": ("filename", file, "python_logo.jpg")},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["avatar"] == new_avatar
    assert "id" in data