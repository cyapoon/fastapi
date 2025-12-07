from fastapi.testclient import TestClient
from app.database import get_db, Base
from app.main import app
import dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from app.oauth2 import create_access_token
from app import models

dotenv.load_dotenv()
DB_PWD = os.getenv("DB_PWD")
DB_USER = os.getenv("DB_USER")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PWD}@{DB_HOST}/{DB_NAME}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        
@pytest.fixture()
def session():
    # drop all tables
    Base.metadata.drop_all(bind=engine)
    # create all tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
           
@pytest.fixture()
def client(session):
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    
@pytest.fixture   
def test_user(client):
    user_data = {"email": "hello123@gmail.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    
    new_user = res.json()
    new_user["password"] = user_data['password']
    return new_user

@pytest.fixture   
def test_user2(client):
    user_data = {"email": "hello234@gmail.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    
    new_user = res.json()
    new_user["password"] = user_data['password']
    return new_user
    
@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})

@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    
    return client

@pytest.fixture
def test_posts(test_user, session, test_user2):
    posts_data = [
        {
            "title": "first title",
            "content": "first content",
            "owner_id": test_user['id']
        },
        {
            "title": "second title",
            "content": "second content",
            "owner_id": test_user['id']
        },
        {
            "title": "thrid title",
            "content": "third content",
            "owner_id": test_user['id']
        },
        {
            "title": "4th title",
            "content": "4th content",
            "owner_id": test_user2['id']
        }
    ]
    
    session.add_all([models.Post(**post) for post in posts_data])
    session.commit()
    posts = session.query(models.Post).all()
    return posts
