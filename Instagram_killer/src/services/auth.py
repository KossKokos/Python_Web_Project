from datetime import datetime, timedelta
from typing import Optional
import pickle

import redis.asyncio as redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session


from src.repository import users as repository_auth
from src.database.db import get_db
from src.conf.config import settings


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
    r_cashe = redis.Redis(host=settings.redis_host, port=settings.redis_port, password=settings.redis_password)

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function takes a plain-text password and the hashed version of that password,
            and returns True if they match, False otherwise. This is used to verify that the user's login
            credentials are correct.
        
        :param self: Represent the instance of the class
        :param plain_password: Pass the password that is being checked
        :param hashed_password: Compare the hashed password in the database with a plain text password
        :return: A boolean value
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password as input and returns the hash of that password.
            The function uses the pwd_context object to generate a hash from the given password.
        
        :param self: Represent the instance of the class
        :param password: str: Get the password from the user
        :return: A hashed password
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_access_token function creates a new access token for the user.
            
        
        :param self: Represent the instance of the class
        :param data: dict: Pass the data that will be encoded into the access token
        :param expires_delta: Optional[float]: Set the expiration time of the access token
        :return: A token in bytes
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=60)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token
    
    def sync_create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_access_token function creates a new access token for the user.
            
        
        :param self: Represent the instance of the class
        :param data: dict: Pass the data that will be encoded into the access token
        :param expires_delta: Optional[float]: Set the expiration time of the access token
        :return: A token in bytes
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=60)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_refresh_token function creates a refresh token for the user.
            Args:
                data (dict): A dictionary containing the user's id and username.
                expires_delta (Optional[float]): The number of seconds until the refresh token expires. Defaults to None, which sets it to 7 days from now.
        
        :param self: Represent the instance of the class
        :param data: dict: Pass in the user's username(email)
        :param expires_delta: Optional[float]: Set the expiration time of the refresh token
        :return: A jwt token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token


    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        The get_current_user function is a dependency that will be used in the UserResource class.
        It takes an access token as input and returns the user object associated with it.
        If no user is found, it raises an HTTPException.
        
        :param self: Access the class attributes and methods
        :param token: str: Get the token from the request header
        :param db: Session: Get the database session
        :return: A user object
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") == "access_token":
                email = payload.get("sub")
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await self.r_cashe.get(f'user: {email}')
        if user is None:
            user = await repository_auth.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            await self.r_cashe.set(f'user: {email}', pickle.dumps(user))
            await self.r_cashe.expire(f'user: {email}', 900)
        else:
            user = pickle.loads(user)
        return user


    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function takes a refresh token and decodes it.
            If the scope is 'refresh_token', then we return the email address of the user.
            Otherwise, we raise an HTTPException with status code 401 (UNAUTHORIZED) and detail message 'Invalid scope for token'.
        
        
        :param self: Represent the instance of the class
        :param refresh_token: str: Pass the refresh token to the function
        :return: The email of the user
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
        

    async def create_email_token(self, data: dict):
        """
        The create_email_token function takes a dictionary of data and returns a JWT token.
        The token is encoded with the SECRET_KEY and ALGORITHM defined in the class.
        The iat (issued at) claim is set to datetime.utcnow() and exp (expiration time) 
        is set to 7 days from now.
        
        :param self: Represent the instance of the class
        :param data: dict: Pass the data that will be encoded in the token
        :return: A token, which is a string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token
    

    def sync_create_email_token(self, data: dict): # for tests
        """
        The create_email_token function takes a dictionary of data and returns a JWT token.
        The token is encoded with the SECRET_KEY and ALGORITHM defined in the class.
        The iat (issued at) claim is set to datetime.utcnow() and exp (expiration time) 
        is set to 7 days from now.
        
        :param self: Represent the instance of the class
        :param data: dict: Pass the data that will be encoded in the token
        :return: A token, which is a string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token


    async def decode_email_token(self, email_token: str):
        """
        The decode_email_token function takes a token as an argument and returns the email address associated with that token.
        If the token is invalid, it raises an HTTPException.
        
        :param self: Represent the instance of the class
        :param token: str: Pass the token to be decoded
        :return: The email address of the user who requested to reset their password
        """
        try:    
            payload = jwt.decode(email_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'email_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for email token')
        except JWTError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Invalid token for email')

service_auth = Auth()
