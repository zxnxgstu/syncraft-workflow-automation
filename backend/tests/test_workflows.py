def make_workflow(client, headers, name="Test Flow"):
    return client.post("/api/v1/workflows",headers=headers,json={"name":name,"description":"demo","trigger_type":"manual","steps":[
        {"position":0,"step_type":"trigger","name":"Start","config":{}},
        {"position":1,"step_type":"transform","name":"Enrich","config":{"set":{"processed":True}}},
        {"position":2,"step_type":"log","name":"Done","config":{"message":"Finished {{name}}"}}]})


def test_workflow_crud_clone_and_owner_scope(client, auth):
    r=make_workflow(client,auth["headers"]); assert r.status_code==201
    wid=r.json()["id"]; assert len(r.json()["steps"])==3
    assert client.get("/api/v1/workflows",headers=auth["headers"]).status_code==200
    patch=client.patch(f"/api/v1/workflows/{wid}",headers=auth["headers"],json={"name":"Updated Flow"}); assert patch.json()["name"]=="Updated Flow"
    clone=client.post(f"/api/v1/workflows/{wid}/clone",headers=auth["headers"]); assert clone.status_code==201 and clone.json()["active"] is False
    other=client.post("/api/v1/auth/register",json={"email":"other@example.com","password":"Password123!"}).json()
    oh={"Authorization":f"Bearer {other['access_token']}"}
    assert client.get(f"/api/v1/workflows/{wid}",headers=oh).status_code==404
    assert client.delete(f"/api/v1/workflows/{wid}",headers=auth["headers"]).status_code==204


def test_manual_execution_transform_and_logs(client, auth):
    wf=make_workflow(client,auth["headers"],"Runnable").json()
    r=client.post(f"/api/v1/executions/workflow/{wf['id']}/run",headers=auth["headers"],json={"payload":{"name":"Alice"}})
    assert r.status_code==200
    body=r.json(); assert body["status"]=="success"; assert body["output_data"]["processed"] is True; assert len(body["logs"])>=3
    listing=client.get("/api/v1/executions",headers=auth["headers"]); assert listing.status_code==200 and listing.json()[0]["workflow_name"]=="Runnable"


def test_webhook_execution(client, auth):
    r=client.post("/api/v1/workflows",headers=auth["headers"],json={"name":"Hook","trigger_type":"webhook","steps":[
        {"step_type":"trigger","name":"Webhook","config":{}},{"step_type":"transform","name":"Mark","config":{"set":{"via":"webhook"}}}]})
    wf=r.json(); hook=client.post(f"/api/v1/hooks/{wf['webhook_token']}",json={"message":"hello"})
    assert hook.status_code==200 and hook.json()["status"]=="success"
