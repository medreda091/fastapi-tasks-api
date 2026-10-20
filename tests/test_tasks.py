"""Tests for the task CRUD endpoints, including per-user isolation."""


def _create(client, headers, title="Buy milk", description="2L whole milk"):
    resp = client.post(
        "/tasks/",
        json={"title": title, "description": description},
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_create_task(client, auth_headers):
    task = _create(client, auth_headers)
    assert task["title"] == "Buy milk"
    assert task["description"] == "2L whole milk"
    assert task["done"] is False
    assert "id" in task


def test_create_task_unauthenticated(client):
    resp = client.post("/tasks/", json={"title": "Nope"})
    assert resp.status_code == 401


def test_create_task_validation(client, auth_headers):
    resp = client.post("/tasks/", json={"title": ""}, headers=auth_headers)
    assert resp.status_code == 422


def test_list_tasks_empty(client, auth_headers):
    resp = client.get("/tasks/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_tasks_only_own(client, auth_headers, other_auth_headers):
    _create(client, auth_headers, title="Alice task")
    _create(client, other_auth_headers, title="Bob task")

    resp = client.get("/tasks/", headers=auth_headers)
    assert resp.status_code == 200
    tasks = resp.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Alice task"


def test_list_tasks_filter_done(client, auth_headers):
    t1 = _create(client, auth_headers, title="open")
    _create(client, auth_headers, title="closed")
    client.put(f"/tasks/{t1['id']}", json={"done": True}, headers=auth_headers)

    resp = client.get("/tasks/", params={"done": True}, headers=auth_headers)
    assert [t["title"] for t in resp.json()] == ["open"]

    resp = client.get("/tasks/", params={"done": False}, headers=auth_headers)
    assert [t["title"] for t in resp.json()] == ["closed"]


def test_get_task(client, auth_headers):
    task = _create(client, auth_headers)
    resp = client.get(f"/tasks/{task['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == task["id"]


def test_get_task_not_found(client, auth_headers):
    resp = client.get("/tasks/9999", headers=auth_headers)
    assert resp.status_code == 404


def test_get_other_users_task_returns_404(client, auth_headers, other_auth_headers):
    task = _create(client, other_auth_headers, title="Bob's secret")
    resp = client.get(f"/tasks/{task['id']}", headers=auth_headers)
    assert resp.status_code == 404


def test_update_task(client, auth_headers):
    task = _create(client, auth_headers)
    resp = client.put(
        f"/tasks/{task['id']}",
        json={"title": "Buy oat milk", "done": True},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "Buy oat milk"
    assert body["done"] is True
    assert body["description"] == "2L whole milk"  # untouched field preserved


def test_update_task_not_found(client, auth_headers):
    resp = client.put("/tasks/9999", json={"done": True}, headers=auth_headers)
    assert resp.status_code == 404


def test_update_other_users_task_returns_404(client, auth_headers, other_auth_headers):
    task = _create(client, other_auth_headers)
    resp = client.put(
        f"/tasks/{task['id']}", json={"done": True}, headers=auth_headers
    )
    assert resp.status_code == 404


def test_delete_task(client, auth_headers):
    task = _create(client, auth_headers)
    resp = client.delete(f"/tasks/{task['id']}", headers=auth_headers)
    assert resp.status_code == 204
    assert client.get(f"/tasks/{task['id']}", headers=auth_headers).status_code == 404


def test_delete_task_not_found(client, auth_headers):
    resp = client.delete("/tasks/9999", headers=auth_headers)
    assert resp.status_code == 404


def test_delete_other_users_task_returns_404(client, auth_headers, other_auth_headers):
    task = _create(client, other_auth_headers)
    resp = client.delete(f"/tasks/{task['id']}", headers=auth_headers)
    assert resp.status_code == 404
    # Bob's task is still there
    assert (
        client.get(f"/tasks/{task['id']}", headers=other_auth_headers).status_code
        == 200
    )


def test_tasks_unauthenticated(client):
    assert client.get("/tasks/").status_code == 401
    assert client.get("/tasks/1").status_code == 401
    assert client.put("/tasks/1", json={"done": True}).status_code == 401
    assert client.delete("/tasks/1").status_code == 401
