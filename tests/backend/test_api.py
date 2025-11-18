"""
Backend API integration tests.

Tests API endpoints with mocked Auth0 authentication.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base
from app.api.deps.db import get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override database dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """Create test client."""
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers():
    """Mock Auth0 headers (for testing without Auth0)."""
    # TODO: Implement proper Auth0 mock or use test tokens
    return {"Authorization": "Bearer mock_token"}

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Garden Platform" in response.json()["service"]

# TODO: Add more tests
# - User profile endpoints
# - Garden/habit endpoints
# - Auth0 token validation
# - Database operations
# - Error handling
