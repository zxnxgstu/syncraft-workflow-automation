def test_register_login_me_and_refresh(client):
    payload={"email":"user@example.com","password":"Password123!","full_name":"User"}
    r=client.post("/api/v1/auth/register",json=payload); assert r.status_code==201
    tokens=r.json(); assert tokens["access_token"] and tokens["refresh_token"]
    me=client.get("/api/v1/auth/me",headers={"Authorization":f"Bearer {tokens['access_token']}"}); assert me.status_code==200
    assert me.json()["email"]==payload["email"]
    login=client.post("/api/v1/auth/login",json={"email":payload["email"],"password":payload["password"]}); assert login.status_code==200
    refresh=client.post("/api/v1/auth/refresh",json={"refresh_token":login.json()["refresh_token"]}); assert refresh.status_code==200


def test_duplicate_and_bad_login(client):
    p={"email":"dup@example.com","password":"Password123!"}
    assert client.post("/api/v1/auth/register",json=p).status_code==201
    assert client.post("/api/v1/auth/register",json=p).status_code==409
    assert client.post("/api/v1/auth/login",json={"email":p["email"],"password":"wrongpass"}).status_code==401


def test_legacy_demo_email_alias(client):
    r=client.post('/api/v1/auth/login',json={'email':'demo@syncraft.local','password':'Syncraft123!'})
    assert r.status_code==200
    assert r.json()['access_token']
