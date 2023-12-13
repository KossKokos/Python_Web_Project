
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

path_root = Path(__file__).parent.parent.parent
sys.path.append(path_root)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.database.models import Base
from src.database.db import get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session):
    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    return {
        "username": "username", 
        "email": "example@example.com", 
        "password": "password"
    }


@pytest.fixture(scope="module")
def user_id_2():
    return {
        "username": "username_2", 
        "email": "example_2@example.com", 
        "password": "password_2"
    }

@pytest.fixture(scope="module")
def user_id_3():
    return {
        "username": "username_3", 
        "email": "example_3@example.com", 
        "password": "password_3"
    }