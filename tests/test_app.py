import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.app import app


def test_home():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200

    data = response.get_json()

    assert data["application"] == "Customer Platform"


def test_health():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code in [200, 500]

    data = response.get_json()

    assert data["status"] in ["UP", "DOWN"]


def test_customer_search_route_exists():
    client = app.test_client()

    response = client.get("/customers/search")

    assert response.status_code in [200, 500]

    data = response.get_json()

    assert data["feature"] == "customer-search"