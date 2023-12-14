import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from src.services.auth import service_auth


"""To start the test, enter : pytest tests/test_services/test_auth.py -v 
You must be in the killer_instagram directory in the console"""


def test_get_password_hash_verify_password_ok():
    password = "password"
    hashed_password = service_auth.get_password_hash(password=password)
    verified_password = service_auth.verify_password(plain_password=password, hashed_password=hashed_password)
    assert verified_password == True

#-----------------------------------------------------------------------------------------------------------------------------------------------

def test_get_password_hash_verify_password_not_ok():
    password = "password"
    other_password = "other_password"
    hashed_password = service_auth.get_password_hash(password=password)
    verified_password = service_auth.verify_password(plain_password=other_password, hashed_password=hashed_password)
    assert verified_password == False

#-----------------------------------------------------------------------------------------------------------------------------------------------
    
@pytest.mark.asyncio
async def test_create_access_token_get_current_user_ok(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        responce = client.post(
            "api/auth/signup",
            json=user
        ) 
        data = responce.json()
        data_for_token = {"sub": data["user"]["email"]}
        access_token = await service_auth.create_access_token(data=data_for_token)
        current_user = await service_auth.get_current_user(token=access_token, db=session)
        assert current_user.username == data["user"]["username"]
        assert current_user.email == data["user"]["email"]

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_access_token_get_current_user_not_found(session):
    not_exciting_email = "not exciting email"
    data_for_token = {"sub": not_exciting_email}
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        access_token = await service_auth.create_access_token(data=data_for_token)
        with pytest.raises(HTTPException) as excinfo:
            await service_auth.get_current_user(token=access_token, db=session)
        assert isinstance(excinfo.value, HTTPException)
        assert excinfo.value.status_code == 401
        assert excinfo.value.detail == "Could not validate credentials"

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_access_token_get_current_user_wrong_token_format(session):
    not_exciting_email = "not exciting email"
    data_for_token = {"sub": not_exciting_email}
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        access_token = await service_auth.create_email_token(data=data_for_token)
        with pytest.raises(HTTPException) as excinfo:
            await service_auth.get_current_user(token=access_token, db=session)
        assert isinstance(excinfo.value, HTTPException)
        assert excinfo.value.status_code == 401
        assert excinfo.value.detail == "Could not validate credentials"

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_refresh_token_decode_refresh_token_ok(user):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        data_for_token = {"sub": user["email"]}
        refresh_token = await service_auth.create_refresh_token(data=data_for_token)
        decoded_token = await service_auth.decode_refresh_token(refresh_token=refresh_token)
        assert decoded_token == data_for_token["sub"]

#-----------------------------------------------------------------------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_refresh_token_decode_refresh_token_wrong_token(user):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        data_for_token = {"sub": user["email"]}
        refresh_token = await service_auth.create_access_token(data=data_for_token)
        with pytest.raises(HTTPException) as excinfo:
            await service_auth.decode_refresh_token(refresh_token=refresh_token)
        assert excinfo.value.status_code == 401
        assert excinfo.value.detail == "Invalid scope for token"

#-----------------------------------------------------------------------------------------------------------------------------------------------
        
@pytest.mark.asyncio
async def test_create_email_token_decode_email_token_ok(user):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        data_for_token = {"sub": user["email"]}
        email_token = await service_auth.create_email_token(data=data_for_token)
        decoded_token = await service_auth.decode_email_token(email_token=email_token)
        assert decoded_token == data_for_token["sub"]

#-----------------------------------------------------------------------------------------------------------------------------------------------
        
@pytest.mark.asyncio
async def test_create_email_token_decode_email_token_wrong_scope(user):
    with patch.object(service_auth, 'r_cashe') as r_mock:
        r_mock.get.return_value = None
        data_for_token = {"sub": user["email"]}
        access_token = await service_auth.create_access_token(data=data_for_token)
        with pytest.raises(HTTPException) as excinfo:
            await service_auth.decode_email_token(email_token=access_token)
        assert excinfo.value.status_code == 401
        assert excinfo.value.detail == "Invalid scope for email token"