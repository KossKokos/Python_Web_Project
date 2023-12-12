import sys
from pathlib import Path
# pytest tests/test_routes/test_auth.py -v
path_root = Path(__file__).parent.parent
sys.path.append(str(path_root))

import pytest
from unittest.mock import MagicMock, patch
from jose import jwt 

from src.database.models import User
from src.services.auth import service_auth
from src.conf.config import settings


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert "id" in data["user"]

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_create_user_again(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data['detail'] == f'User with email: {user["email"]} already exists'

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_login_user_not_confirmed(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email is not confirmed"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_login_user(client, session, user):
    current_user: User = session.query(User).filter(User.email==user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 202, response.text
    data = response.json()
    assert data["token_type"] == "bearer"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_login_wrong_password(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": 'wrong password'},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_login_wrong_email(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": 'email', "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope='function')
def login(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user['email'], "password": user['password']},
    )
    data = response.json()
    return data

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_refresh_token_200(client, login):
    old_refresh_token = login['refresh_token']
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/auth/refresh_token",
            headers={"Authorization": f"Bearer {old_refresh_token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data['token_type'] == 'bearer'

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_refresh_token_not_token(client):
    old_refresh_token = "wrong refresh token"
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/auth/refresh_token",
            headers={"Authorization": f"Bearer {old_refresh_token}"}
        )
        assert response.status_code == 401, response.text
        data = response.json()
        assert data['detail'] == "Could not validate credentials"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_refresh_token_access_token(client, login):
    old_refresh_token = login["access_token"]
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/auth/refresh_token",
            headers={"Authorization": f"Bearer {old_refresh_token}"}
        )
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == "Invalid scope for token"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_refresh_token_access_token(client, login):
    old_refresh_token = login["refresh_token"]
    payload = jwt.decode(old_refresh_token, settings.secret_key, algorithms=[settings.algorithm])
    payload['sub'] = "wrong email"
    wrong_refresh_token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/auth/refresh_token",
            headers={"Authorization": f"Bearer {wrong_refresh_token}"}
        )
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == "User with this token doesn't exist"

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope='function')
async def get_email_token(client, new_user, monkeypatch) -> str:
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=new_user,
    )
    data = response.json()
    user = data["user"]
    email = user["email"]
    email_token = await service_auth.create_email_token({"sub": email})
    return email_token

#-----------------------------------------------------------------------------------------------------------------------------------------------

async def test_confirmed_email_ok(client, get_email_token):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        email_token = await get_email_token
        response = client.get(
            f"/api/auth/confirmed_email/{email_token}"
        )
        assert response.status_code == 202, response.text
        data = response.json()
        assert data["detail"] == "Email is confirmed'"

#-----------------------------------------------------------------------------------------------------------------------------------------------

