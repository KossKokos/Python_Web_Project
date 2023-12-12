import sys
import asyncio
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
from src.schemas.email import RequestEmail
from src.repository.users import get_user_by_email

pytest_plugins = ('pytest_asyncio',)


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
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        payload = jwt.decode(old_refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        payload['sub'] = "wrong email"
        wrong_refresh_token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
        response = client.get(
            "/api/auth/refresh_token",
            headers={"Authorization": f"Bearer {wrong_refresh_token}"}
        )
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == "User with this token doesn't exist"

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope='function')
def get_email_from_signup(client, new_user, monkeypatch) -> str:
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=new_user,
    )
    data: dict = response.json()
    user: dict = data["user"]
    email: str = user["email"]
    return email

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_request_email_ok(client, get_email_from_signup, monkeypatch):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        mock_send_email = MagicMock()
        monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
        body: dict = {"email": get_email_from_signup}
        response = client.post(
            "api/auth/request_email",
            json=body
        )    
        assert response.status_code == 202, response.text
        data: dict = response.json()
        assert data["detail"] == "Check your email for further information"
    
#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="function")
def get_email_token(new_user) -> str:
    data: dict = {"sub": new_user["email"]}
    email_token = service_auth.sync_create_email_token(data=data)
    return email_token

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_confirmed_email_ok(client, get_email_token):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/auth/confirmed_email/{get_email_token}"
        )
        assert response.status_code == 202, response.text
        data = response.json()
        assert data["detail"] == "Email is confirmed"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_request_email_again(client, new_user, monkeypatch):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        mock_send_email = MagicMock()
        monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
        body: dict = {"email": new_user["email"]}
        response = client.post(
            "api/auth/request_email",
            json=body
        )    
        assert response.status_code == 202, response.text
        data: dict = response.json()
        assert data["detail"] == "Email is already confirmed"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_confirmed_email_wrong_token(client):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/auth/confirmed_email/email_token"
        )
        assert response.status_code == 422, response.text
        data = response.json()
        assert data["detail"] == "Invalid token for email"

#-----------------------------------------------------------------------------------------------------------------------------------------------
@pytest.fixture(scope="function")
def no_user_email_token():
    wrong_email = "wrong_email@example.com"
    email_token = service_auth.sync_create_email_token({"sub": wrong_email})
    return email_token

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_confirmed_email_no_user(client, no_user_email_token):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/auth/confirmed_email/{no_user_email_token}"
        )
        assert response.status_code == 400, response.text
        data = response.json()
        assert data["detail"] == "Verification error"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_request_reset_password_email(client, new_user, monkeypatch):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        mock_send_email = MagicMock()
        monkeypatch.setattr("src.routes.auth.send_reset_password_email", mock_send_email)
        body: dict = {"email": new_user["email"]}
        response = client.post(
            "api/auth/reset_password",
            json=body
        )    
        assert response.status_code == 202, response.text
        data: dict = response.json()
        assert data["detail"] == "Check your email for further information"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_reset_password_no_user(client, no_user_email_token):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        body: dict = {"new_password": "new_password"}
        response = client.patch(
            f"api/auth/change_password/{no_user_email_token}",
            json=body
        )    
        assert response.status_code == 400, response.text
        data: dict = response.json()
        assert data["detail"] == "Verification error"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_reset_password(client, get_email_token):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        body: dict = {"new_password": "new_password"}
        response = client.patch(
            f"api/auth/change_password/{get_email_token}",
            json=body
        )    
        assert response.status_code == 202, response.text
        data: dict = response.json()
        assert data["detail"] == "User's password was changed succesfully"
