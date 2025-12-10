import pytest
from fastapi.testclient import TestClient
from urllib.parse import quote

from src.app import app


client = TestClient(app)


def test_root_redirect():
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (302, 307)
    assert resp.headers.get("location") == "/static/index.html"


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Basic sanity check for one known activity
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "testuser@example.com"

    # Sign up
    signup_resp = client.post(f"/activities/{quote(activity)}/signup?email={email}")
    assert signup_resp.status_code == 200
    assert "Signed up" in signup_resp.json().get("message", "")

    # Verify participant appears
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]

    # Unregister
    unreg_resp = client.post(f"/activities/{quote(activity)}/unregister?email={email}")
    assert unreg_resp.status_code == 200
    assert "Unregistered" in unreg_resp.json().get("message", "")

    # Verify participant removed
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]
