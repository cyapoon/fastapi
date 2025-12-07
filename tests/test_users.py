from app import schemas
from jose import jwt
import pytest
from dotenv import load_dotenv
load_dotenv()
import os
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("HS256")



def test_root(client):
    res = client.get("/")
    assert res.json().get("message") == "Hello, World"
    assert res.status_code == 200
    
def test_create_user(client):
    res = client.post("/users/", json={"email": "hello123@gmail.com", "password": "asd123"})
    # print(res.json())'
    new_user = schemas.UserOut(**res.json())
    assert new_user.email == "hello123@gmail.com"
    assert res.status_code == 201
    
def test_login_user(client, test_user):
    res = client.post("/login/", data={"username": test_user['email'], "password": test_user['password']})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, SECRET_KEY, ALGORITHM)
    id = payload.get("user_id")
    assert res.status_code == 200
    assert login_res.token_type == "bearer"
    assert id == test_user['id']
    
@pytest.mark.parametrize("email, password, status_code", [
    ("wrongEmail", "password123", 403),
    ("hello123@gmail.com", "wrongPassword", 403),
    (None, "password123", 403),
    ("hello123@gmail.com", None, 403)
])
def test_incorrect_login(test_user, client, email, password, status_code):
    # print({"username": email, "password": password})
    res = client.post("/login/", data={"username": email, "password": password})
    
    assert res.status_code == status_code