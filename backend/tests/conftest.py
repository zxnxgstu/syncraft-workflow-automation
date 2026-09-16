import os
os.environ["DATABASE_URL"] = "sqlite:///./test_syncraft.db"
os.environ["JWT_SECRET"] = "test-secret-with-at-least-32-bytes-long"

import pytest
from fastapi.testclient import TestClient
from app.db.base import Base
from app.db.session import engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth(client):
    email = "tester@example.com"
    password = "StrongPass123!"
    r = client.post("/api/v1/auth/register", json={"email": email, "password": password, "full_name": "Tester"})
    assert r.status_code == 201
    tokens = r.json()
    return {"headers": {"Authorization": f"Bearer {tokens['access_token']}"}, "tokens": tokens, "email": email, "password": password}
