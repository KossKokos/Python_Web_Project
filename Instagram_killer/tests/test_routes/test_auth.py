import sys
from pathlib import Path

path_root = Path(__file__).parent.parent
sys.path.append(str(path_root))

import pytest
from unittest.mock import MagicMock, patch
from jose import jwt 

from src.database.models import User
from src.services.auth import service_auth
from src.conf.config import settings


"""To start the test, enter : pytest tests/test_routes/test_auth.py -v 
You must be in the killer_instagram directory in the console"""


"""Fixtures:"""

@pytest.fixture(scope='function')
def super_admin_login(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    data = response.json()
    return data

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope='function')
def admin_login(client, user_id_2):
    login_response = client.post(
        "/api/auth/login",
        data={"username": user_id_2["email"], "password": "new_password"},
    )
    data = login_response.json()
    return data

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope='function')
def user_id_3_role_admin(client, user_id_3, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.service_email.send_email", mock_send_email)
    signup_response = client.post(
        "/api/auth/signup",
        json=user_id_3,
    )
    user: User = session.query(User).filter(User.email==user_id_3["email"]).first()
    user.role = "admin"
    session.commit()
    data = signup_response.json()
    return data

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope='function')
def get_email_from_signup(client, user_id_2, monkeypatch) -> str:
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.service_email.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user_id_2,
    )
    data: dict = response.json()
    user: dict = data["user"]
    email: str = user["email"]
    return email

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="function")
def get_email_token(user_id_2) -> str:
    data: dict = {"sub": user_id_2["email"]}
    email_token = service_auth.sync_create_email_token(data=data)
    return email_token

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="function")
def no_user_email_token():
    wrong_email = "wrong_email@example.com"
    email_token = service_auth.sync_create_email_token({"sub": wrong_email})
    return email_token

#-----------------------------------------------------------------------------------------------------------------------------------------------


"""Tests:"""

def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.service_email.send_email", mock_send_email)
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
    monkeypatch.setattr("src.routes.auth.service_email.send_email", mock_send_email)
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

def test_refresh_token_200(client, super_admin_login):
    old_refresh_token = super_admin_login['access_token']
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

def test_refresh_token_wrong_scope(client, super_admin_login):
    old_refresh_token = super_admin_login["refresh_token"]
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/auth/refresh_token",
            headers={"Authorization": f"Bearer {old_refresh_token}"}
        )
        assert response.status_code == 401, response.text
        data = response.json()
        assert data["detail"] == "Could not validate credentials"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_refresh_token_access_token(client, super_admin_login):
    old_refresh_token = super_admin_login["refresh_token"]
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
        assert data["detail"] == "Could not validate credentials"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_request_email_ok(client, get_email_from_signup, monkeypatch):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        mock_send_email = MagicMock()
        monkeypatch.setattr("src.routes.auth.service_email.send_email", mock_send_email)
        body: dict = {"email": get_email_from_signup}
        response = client.post(
            "api/auth/request_email",
            json=body
        )    
        assert response.status_code == 202, response.text
        data: dict = response.json()
        assert data["detail"] == "Check your email for further information"
    
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

def test_request_email_again(client, user_id_2, monkeypatch):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        mock_send_email = MagicMock()
        monkeypatch.setattr("src.routes.auth.service_email.send_email", mock_send_email)
        body: dict = {"email": user_id_2["email"]}
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

def test_request_reset_password_email(client, user_id_2, monkeypatch):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        mock_send_email = MagicMock()
        monkeypatch.setattr("src.routes.auth.service_email.send_reset_password_email", mock_send_email)
        body: dict = {"email": user_id_2["email"]}
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

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_change_role_not_admin(client, admin_login):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        token: str = admin_login["access_token"]
        body: dict = {"role": "moderator"}
        response = client.patch(
            f"api/auth/change_role/{1}",
            json=body,
            headers={"Authorization": f"Bearer {token}"}
        )    
        assert response.status_code == 403, response.text
        data: dict = response.json()
        assert data["detail"] == "Operation forbidden for user"

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_change_role_no_user(client, super_admin_login):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        token: str = super_admin_login["access_token"]
        body: dict = {"role": "admin"}
        response = client.patch(
            f"api/auth/change_role/{10}",
            json=body,
            headers={"Authorization": f"Bearer {token}"}
        )    
        assert response.status_code == 404, response.text
        data: dict = response.json()
        assert data["detail"] == "User not found"
        
#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_change_role_own_role(client, super_admin_login):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        token: str = super_admin_login["access_token"]
        body: dict = {"role": "moderator"}
        response = client.patch(
            f"api/auth/change_role/{1}",
            json=body,
            headers={"Authorization": f"Bearer {token}"}
        )    
        assert response.status_code == 403, response.text
        data: dict = response.json()
        assert data["detail"] == "Permission denied. Own role cannot be changed."

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_change_role_ok(client, super_admin_login, user_id_2, session):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        token: str = super_admin_login["access_token"]
        body: dict = {"role": "admin"}
        response = client.patch(
            f"api/auth/change_role/{2}",
            json=body,
            headers={"Authorization": f"Bearer {token}"}
        )   
        current_user: User = session.query(User).filter(User.email==user_id_2.get('email')).first()
        current_user.role = body["role"]
        session.commit() 
        assert response.status_code == 202, response.text
        data: dict = response.json()
        assert data["username"] == user_id_2["username"]
        assert data["role"] == body["role"]

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_change_role_not_superadmin(client, admin_login, user_id_3_role_admin):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        token: str = admin_login["access_token"]
        body: dict = {"role": "moderator"}
        user_id: int = 3
        response = client.patch(
            f"api/auth/change_role/{user_id}",
            json=body,
            headers={"Authorization": f"Bearer {token}"}
        )    
        assert response.status_code == 403, response.text
        data: dict = response.json()
        assert data["detail"] == "Permission denied.Admin role can be changed only by Superadmin (id=1)."

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_change_role_role_not_found(client, super_admin_login):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        token: str = super_admin_login["access_token"]
        body: dict = {"role": "wrong role"}
        user_id: int = 2
        response = client.patch(
            f"api/auth/change_role/{user_id}",
            json=body,
            headers={"Authorization": f"Bearer {token}"}
        )    
        assert response.status_code == 400, response.text
        data: dict = response.json()
        assert data["detail"] == "Invalid role provided"