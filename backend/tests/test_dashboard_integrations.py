def test_dashboard_templates_and_integrations(client, auth):
    response=client.get("/api/v1/dashboard",headers=auth["headers"])
    assert response.status_code==200
    dashboard=response.json(); metrics=dashboard["metrics"]; activity=dashboard["execution_activity"]
    assert metrics["total_executions"] == metrics["success_executions"] + metrics["failed_executions"]
    assert len(activity) == metrics["total_executions"]
    assert sum(row["status"] == "success" for row in activity) == metrics["success_executions"]
    assert sum(row["status"] == "failed" for row in activity) == metrics["failed_executions"]
    expected_rate=round(metrics["success_executions"] / metrics["total_executions"] * 100, 1) if metrics["total_executions"] else 0
    assert metrics["success_rate"] == expected_rate
    templates=client.get("/api/v1/templates",headers=auth["headers"]); assert templates.status_code==200 and len(templates.json())>=3
    integrations=client.get("/api/v1/integrations",headers=auth["headers"]); assert integrations.status_code==200 and len(integrations.json())>=5
    updated=client.put("/api/v1/integrations/telegram",headers=auth["headers"],json={"connected":True,"config":{}})
    assert updated.status_code==200 and updated.json()["connected"] is True


def test_health(client):
    assert client.get("/health").json()["status"]=="ok"
    assert client.get("/ready").status_code==200
