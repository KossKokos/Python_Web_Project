import os

from dotenv import load_dotenv
from pydantic import BaseSettings, EmailStr

load_dotenv()

class Settings(BaseSettings):
    sqlalchemy_database_url: str = os.environ.get('SQLALCHEMY_DATABASE_URL')
    secret_key: str = os.environ.get('SECRET_KEY')
    algorithm: str = os.environ.get('ALGORITHM')
    mail_username: str = os.environ.get('MAIL_USERNAME')
    mail_password: str = os.environ.get('MAIL_PASSWORD')
    mail_from: EmailStr = os.environ.get('MAIL_FROM')
    mail_port: int = os.environ.get('MAIL_PORT')
    mail_server: str = os.environ.get('MAIL_SERVER')
    cloudinary_name: str = os.environ.get('CLOUDINARY_NAME')
    cloudinary_api_key: str = os.environ.get('CLOUDINARY_API_KEY')
    cloudinary_api_secret: str = os.environ.get('CLOUDINARY_API_SECRET')
    redis_name: str = os.environ.get('REDIS_NAME')
    redis_password: str = os.environ.get('REDIS_PASSWORD')
    redis_host: str = os.environ.get('REDIS_HOST')
    redis_port: int = os.environ.get('REDIS_PORT')
    redis_db: int = os.environ.get('REDIS_DB')

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
