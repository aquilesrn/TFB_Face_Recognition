import pytest
from sqlalchemy import text
from app.database import SessionLocal, get_db

def test_database_connection():
    try:
        session = SessionLocal()
        session.execute(text("SELECT 1"))
        session.close()
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")

def test_get_db():
    try:
        generator = get_db()
        session = next(generator)
        assert session is not None
        session.close()
    except Exception as e:
        pytest.fail(f"get_db failed: {e}")
