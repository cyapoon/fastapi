from fastapi.testclient import TestClient
from app.database import get_db, Base
from app.main import app
import dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

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