import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.user import Base
from app.core.database import get_db
from app.services.auth_service import create_user, get_users, get_user_by_username, get_user_by_email
from app.schemas.user import UserCreate
import os

# Test database setup - Use SQLite for tests
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./test.db"
SQLALCHEMY_DATABASE_URL = DATABASE_URL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def setup_database():
    """Set up test database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_user():
    """Test creating a new user."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User"
    }

    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data


def test_create_user_duplicate_username():
    """Test creating a user with duplicate username."""
    user_data = {
        "email": "test2@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User 2"
    }

    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_get_users():
    """Test getting all users."""
    # First create a user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User"
    }
    client.post("/api/v1/users/", json=user_data)

    response = client.get("/api/v1/users/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_user_by_username():
    """Test getting a user by username."""
    # First create a user
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User"
    }
    client.post("/api/v1/users/", json=user_data)

    response = client.get("/api/v1/users/testuser")
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_get_nonexistent_user():
    """Test getting a nonexistent user."""
    response = client.get("/api/v1/users/nonexistent")
    assert response.status_code == 404


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


def test_detailed_health_check():
    """Test detailed health check endpoint."""
    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data
    assert data["services"]["api"] == "running"
