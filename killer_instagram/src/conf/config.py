import os

from dotenv import load_dotenv
from pydantic import BaseSettings, EmailStr

load_dotenv(verbose=True) 

class Settings(BaseSettings):
    sqlalchemy_database_url: str = os.getenv("SQLALCHEMY_DATABASE_URL")
    secret_key: str = os.getenv("SECRET_KEY")
    algorithm: str = os.getenv("ALGORITHM")
    mail_username: str = os.getenv("MAIL_USERNAME")
    mail_password: str = os.getenv("MAIL_PASSWORD")
    mail_from: EmailStr = os.getenv("MAIL_FROM")
    mail_port: int = os.getenv("MAIL_PORT")
    mail_server: str = os.getenv("MAIL_SERVER")
    cloudinary_name: str = os.getenv("CLOUDINARY_NAME")
    cloudinary_api_key: str = os.getenv("CLOUDINARY_API_KEY")
    cloudinary_api_secret: str = os.getenv("CLOUDINARY_API_SECRET")
    redis_name: str = os.getenv("REDIS_NAME")
    redis_host: str = os.getenv("REDIS_HOST")
    redis_port: int = os.getenv("REDIS_PORT")
    redis_db: int = os.getenv("REDIS_DB")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive=False

settings = Settings()
