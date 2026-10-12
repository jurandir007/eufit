# EUFit/tests/test_social.py
import pytest
from app import create_app
from config import TestConfig


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_social_home_status_and_content(client):
    response = client.get("/social/")
    assert response.status_code == 200
    assert b"ConnectHub" in response.data
    assert b"PostgreSQL Neon: Database Social" in response.data


def test_social_queries_status_and_content(client):
    response = client.get("/social/queries")
    assert response.status_code == 200
    assert b"Consultas Anal" in response.data
    assert b"Query 1: Timeline" in response.data
    assert b"Query 2: M" in response.data
