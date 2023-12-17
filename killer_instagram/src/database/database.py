from contextlib import contextmanager
from sqlalchemy.orm import Session

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
