import io
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app  # noqa: E402


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_cors_allows_configured_origin(client):
    res = client.get("/health", headers={"Origin": "http://localhost:8000"})
    assert res.headers.get("Access-Control-Allow-Origin") == "http://localhost:8000"


def test_cors_blocks_unknown_origin(client):
    res = client.get("/health", headers={"Origin": "https://evil.example.com"})
    assert "Access-Control-Allow-Origin" not in res.headers


def test_home_missing_fields(client):
    assert client.post("/generate-home", json={}).status_code == 400


def test_home_negative_budget_rejected(client):
    res = client.post("/generate-home", json={"budget": -5, "details": "sofa"})
    assert res.status_code == 400


def test_home_non_numeric_budget_rejected(client):
    res = client.post("/generate-home", json={"budget": "abc", "details": "sofa"})
    assert res.status_code == 400


def test_home_returns_recommendation(client):
    # Without a real key this uses the fallback path but still returns 200.
    res = client.post(
        "/generate-home",
        json={"budget": 20000, "details": "1 bedroom, needs a bed and wardrobe"},
    )
    assert res.status_code == 200
    body = res.get_json()
    assert body["recommendation"]
    assert "suggested_products" in body


def test_party_missing_fields(client):
    assert client.post("/generate-party", json={"budget": 5000}).status_code == 400


def test_party_ok(client):
    res = client.post(
        "/generate-party", json={"budget": 8000, "event_type": "Birthday", "guests": 20}
    )
    assert res.status_code == 200


def test_jewelry_missing_fields(client):
    assert client.post("/generate-jewelry", data={}).status_code == 400


def test_jewelry_bad_extension_rejected(client):
    res = client.post(
        "/generate-jewelry",
        data={
            "budget": "5000",
            "occasion": "Festive",
            "outfit_image": (io.BytesIO(b"x"), "outfit.exe"),
        },
        content_type="multipart/form-data",
    )
    assert res.status_code == 400


def test_jewelry_broken_image_falls_back(client):
    res = client.post(
        "/generate-jewelry",
        data={
            "budget": "5000",
            "occasion": "Festive",
            "outfit_image": (io.BytesIO(b"not a real image"), "outfit.jpg"),
        },
        content_type="multipart/form-data",
    )
    assert res.status_code == 200
    # uploaded file must be cleaned up
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    leftovers = [f for f in os.listdir(upload_dir) if f != ".gitkeep"]
    assert leftovers == []
