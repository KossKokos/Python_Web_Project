import sys
from pathlib import Path
import json
# path_root = Path(__file__).parent.parent
# sys.path.append(str(path_root))

import pytest
from unittest.mock import MagicMock, patch
from jose import jwt 
from fastapi import File

from src.database.models import User
from src.services.auth import service_auth
from src.conf.config import settings


"""To run tests, enter: pytest tests/test_routes/test_users.py -v
in the killer_instagram directory in console"""

#-----------------------------------------------------------------------------------------------------------------------------------------------
"""Fixtures:"""

@pytest.fixture(scope="function")
def access_token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
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
    token = service_auth.sync_create_email_token(data=data)
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
        assert response.status_code == 202, response.text
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

def test_update_avatar_ok(client, access_token, monkeypatch):
    mock_cloud_service = MagicMock()
    mock_publick_id = mock_cloud_service.return_value = "publick_id"
    mock_cloud = mock_cloud_service.re = "cloud"
    mock_build_url = mock_cloud_service.re = "some url"
    monkeypatch.setattr("src.routes.users.CloudImage.generate_name_avatar", mock_publick_id)
    monkeypatch.setattr("src.routes.users.CloudImage.upload", mock_cloud)
    monkeypatch.setattr("src.routes.users.CloudImage.get_url", mock_build_url)
    # file = open("tests/python_logo.jpg", "r")
    mock_image = MagicMock(file=File())
    mock_image.file = "python_logo.jpg"
    file_path = r"C:\Users\kosko\Documents\Python\Python_Web\Final_project\Killer_instagram\killer_instagram\tests\test_routes\python_logo.jpg"
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        with open(file_path, "wb") as fd:
            response = client.patch(
            "api/users/avatar",
            # {"file": mock_image},
            {"file": ("filename", fd, "python")},
            headers={"Authorization": f"Bearer {access_token}"}
        )
    assert response.status_code == 201, response.text