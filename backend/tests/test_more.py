def create_auth(client, email="more@example.com"):
    data = client.post("/api/v1/auth/register", json={"email": email, "password": "Password123!"}).json()
    return {"Authorization": f"Bearer {data['access_token']}"}, data


def test_auth_required_for_private_endpoints(client):
    for path in ["/api/v1/workflows", "/api/v1/executions", "/api/v1/dashboard", "/api/v1/integrations", "/api/v1/templates"]:
        assert client.get(path).status_code == 401


def test_old_refresh_token_is_revoked_after_rotation(client):
    _, tokens = create_auth(client, "rotate@example.com")
    old = tokens["refresh_token"]
    first = client.post("/api/v1/auth/refresh", json={"refresh_token": old})
    assert first.status_code == 200
    second = client.post("/api/v1/auth/refresh", json={"refresh_token": old})
    assert second.status_code == 401


def test_unknown_webhook_returns_404(client):
    assert client.post("/api/v1/hooks/not-a-real-token", json={"x": 1}).status_code == 404


def test_telegram_step_preview_mode(client):
    headers, _ = create_auth(client, "telegram@example.com")
    wf = client.post("/api/v1/workflows", headers=headers, json={
        "name": "Telegram Preview", "trigger_type": "manual", "steps": [
            {"step_type": "trigger", "name": "Start", "config": {}},
            {"step_type": "telegram", "name": "Notify", "config": {"message": "Hello {{name}}"}},
        ]
    }).json()
    run = client.post(f"/api/v1/executions/workflow/{wf['id']}/run", headers=headers, json={"payload": {"name": "World"}})
    assert run.status_code == 200
    body = run.json()
    assert body["status"] == "success"
    assert body["output_data"]["telegram_preview"] == "Hello World"
    assert any("preview mode" in log["message"] for log in body["logs"])


def test_execution_status_filter(client):
    headers, _ = create_auth(client, "filter@example.com")
    wf = client.post("/api/v1/workflows", headers=headers, json={
        "name": "Filter Flow", "steps": [{"step_type": "trigger", "name": "Start", "config": {}}]
    }).json()
    client.post(f"/api/v1/executions/workflow/{wf['id']}/run", headers=headers, json={"payload": {}})
    success = client.get("/api/v1/executions?status=success", headers=headers)
    failed = client.get("/api/v1/executions?status=failed", headers=headers)
    assert success.status_code == 200 and len(success.json()) >= 1
    assert failed.status_code == 200
    assert all(row["status"] == "failed" for row in failed.json())
