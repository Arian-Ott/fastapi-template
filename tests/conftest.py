import os
import pytest
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from api.main import app
from api.db.session import get_db, Base

# ------------------------
# 🔧 SQLite Test DB Setup
# ------------------------
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ------------------------
# 🔁 Dependency Override
# ------------------------
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply override once at import time
app.dependency_overrides[get_db] = override_get_db

# ------------------------
# 📦 Fixtures
# ------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create the schema once per test session, drop it at the end."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    try:
        os.remove("test.db")
    except FileNotFoundError:
        pass

@pytest.fixture(scope="function")
def db():
    """Provides a clean DB session per test function."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture(scope="function")
def client():
    """FastAPI test client with DB override applied."""
    with TestClient(app) as c:
        yield c