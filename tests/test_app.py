import os

os.environ["IMAGE_BACKEND"] = "placeholder"

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_homepage():
    response = client.get("/")

    assert response.status_code == 200

    assert "ComicCraft" in response.text


def test_docs():
    response = client.get("/docs")

    assert response.status_code == 200


def test_openapi():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    data = response.json()

    assert "paths" in data

    assert "/generate-comic/json" in data["paths"]


def test_test_image():
    response = client.get(
        "/test-image",
        params={
            "prompt": "A small fox"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert "image_url" in data