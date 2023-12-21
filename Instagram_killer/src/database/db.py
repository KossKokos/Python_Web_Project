from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.conf.config import settings


SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    """
    The get_db function opens a new database connection if there is none yet for the current application context.
    It will also create the database tables if they don’t exist yet.
    
    :return: A database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def db_transaction(session: Session):
    """
    The db_transaction function is a context manager that wraps the session object in a try/except block.
    If an exception occurs, it rolls back the transaction and raises the exception. If no exceptions occur,
    it commits the transaction and closes out the session.
    
    :param session: Session: Pass the session object to the function
    :return: A context manager
    """
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()