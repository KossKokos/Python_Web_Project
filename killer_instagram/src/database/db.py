from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.conf.config import settings


SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
print(SQLALCHEMY_DATABASE_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def db_transaction(session: Session):
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()