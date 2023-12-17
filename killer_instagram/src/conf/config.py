from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    sqlalchemy_database_url: str = "postgresql+psycopg2://user:password@host:port/database"
    secret_key: str = 'secret_key'
    algorithm: str = 'algorithm'
    mail_username: str = 'example@com.com'
    mail_password: str = 'mail_password'
    mail_from: EmailStr = 'example@com.com'
    mail_port: int = 666
    mail_server: str = 'mail_server'
    cloudinary_name: str = 'dgfy9rl4j'
    cloudinary_api_key: str = '279781871815418'
    cloudinary_api_secret: str = 'ZrAB5euIOuXbieCTtQjnqjoSpP0'
    redis_name: str = 'redis'
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_db: int = 0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()