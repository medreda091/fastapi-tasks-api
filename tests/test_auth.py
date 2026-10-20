"""Tests for registration, login and the /users/me endpoint."""


def test_register_success(client):
    resp = client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "supersecret1"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "new@example.com"
    assert "id" in body
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "supersecret1"}
    assert client.post("/auth/register", json=payload).status_code == 201
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"]


def test_register_invalid_email(client):
    resp = client.post(
        "/auth/register", json={"email": "not-an-email", "password": "supersecret1"}
    )
    assert resp.status_code == 422


def test_register_short_password(client):
    resp = client.post(
        "/auth/register", json={"email": "short@example.com", "password": "abc"}
    )
    assert resp.status_code == 422


def test_login_success(client):
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "supersecret1"},
    )
    resp = client.post(
        "/auth/login",
        data={"username": "login@example.com", "password": "supersecret1"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={"email": "wrongpw@example.com", "password": "supersecret1"},
    )
    resp = client.post(
        "/auth/login",
        data={"username": "wrongpw@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


def test_login_unknown_user(client):
    resp = client.post(
        "/auth/login",
        data={"username": "ghost@example.com", "password": "whatever123"},
    )
    assert resp.status_code == 401


def test_users_me_authenticated(client, auth_headers):
    resp = client.get("/users/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "alice@example.com"


def test_users_me_unauthenticated(client):
    resp = client.get("/users/me")
    assert resp.status_code == 401


def test_users_me_invalid_token(client):
    resp = client.get("/users/me", headers={"Authorization": "Bearer invalid-token"})
    assert resp.status_code == 401
