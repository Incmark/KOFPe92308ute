import pytest
import pytest_asyncio
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy.pool import NullPool

from app.api.deps import get_db
from app.db.base import Base
from app.models.user import User
from app.models.status import Status
from app.models.service import Service
from app.db.init_db import init_db
from app.main import app


@pytest_asyncio.fixture(scope="session")
async def test_db():
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:1@localhost/sampleserv_test", poolclass=NullPool,)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sess = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with sess() as s:
        await init_db(s)
    yield sess
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(test_db):
    async with test_db() as s:
        yield s
        await s.rollback()
        await s.close()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        try:
            yield db_session
        finally:
            await db_session.rollback()
    app
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_user_and_generate_randint(client: TestClient, db_session: AsyncSession):
    email = "Alice@gmail.com"
    password = "MEGApass"
    response = client.post(
        "/api/v1/auth/signup", json={"email": email, "password": password})
    assert response.status_code == 201
    res = response.json()
    assert res["email"] == email
    response = client.post(
        "/api/v1/auth/login", data={"username": email, "password": password})
    res = response.json()
    token = res["access_token"]
    res = client.get("/api/v1/auth/me",
                     headers={"Authorization": f"Bearer {token}"}).json()
    assert res["email"] == email
    res = client.get("/api/v1/random/int",
                     headers={"Authorization": f"Bearer {token}"}).json()
    assert res["detail"]
    user = await db_session.get(User, 1)
    db_session.add(user)
    user.status_id = 1
    user.status_purchased_time = datetime.utcnow()
    await db_session.commit()
    response = client.get("/api/v1/random/int",
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    res = response.json()
    assert res["value"]


@pytest.mark.asyncio
async def test_unknown_user(client: TestClient, db_session: AsyncSession):
    email = "Alice2@gmail.com"
    password = "MEGApass"
    response = client.post(
        "/api/v1/auth/login", data={"username": email, "password": password})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_randint_access(client: TestClient):
    response = client.get("/api/v1/random/int")
    assert response.status_code == 401
