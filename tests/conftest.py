# backend/tests/conftest.py
import asyncio
import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
import uuid

from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.db.base import Base
from app.main import app as fastapi_app
from app.models.models import User, Role
from app.core.config import settings
from app.db.session import get_async_db

# Override database settings for testing
# Use file-based SQLite for testing
test_db_file = f"test_{uuid.uuid4()}.db"
TEST_SQLALCHEMY_DATABASE_URI = f"sqlite+aiosqlite:///{test_db_file}"

# Create test async engine
test_engine = create_async_engine(
    TEST_SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False},
    echo=True  # Added echo=True to see SQL statements for debugging
)

# Create test async session
TestAsyncSessionLocal = sessionmaker(
    test_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Override the get_async_db dependency to use test database
async def override_get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Test user data
test_user = {
    "email": "test@example.com",
    "password": "password123",
    "is_active": True,
    "role_id": 1,
}

test_superuser = {
    "email": "admin@example.com",
    "password": "adminpass123",
    "is_active": True,
    "is_superuser": True,
    "role_id": 1,
}


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def init_db():
    """Set up the test database"""
    # Create all tables in the test database
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create initial data (roles) that the application needs
    async with TestAsyncSessionLocal() as session:
        admin_role = Role(name="Admin")
        doctor_role = Role(name="Doctor")
        researcher_role = Role(name="Researcher")
        session.add_all([admin_role, doctor_role, researcher_role])
        await session.commit()
    
    yield
    
    # Clean up resources after tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()
    
    # Remove the test database file
    try:
        os.remove(test_db_file)
    except FileNotFoundError:
        pass


@pytest_asyncio.fixture(scope="session")
async def app(init_db) -> FastAPI:
    # Override the get_async_db dependency to use test database
    from app.db.session import get_async_db
    fastapi_app.dependency_overrides[get_async_db] = override_get_async_db
    
    yield fastapi_app


@pytest_asyncio.fixture(scope="function")
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a new FastAPI AsyncClient that uses the `app` fixture to make requests.
    """
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for tests.
    """
    async with TestAsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def registered_user(client: AsyncClient) -> dict:
    """
    Register a test user and return user data.
    If the user already exists, log them in to verify credentials.
    """
    # Try to register the user
    response = await client.post(
        "/auth/register/register", 
        json=test_user,
    )
    
    # If the user already exists, that's fine too
    if response.status_code == 400 and "REGISTER_USER_ALREADY_EXISTS" in response.text:
        # Verify the user by logging in
        login_data = {
            "username": test_user["email"],
            "password": test_user["password"],
        }
        login_response = await client.post("/auth/jwt/login", data=login_data)
        assert login_response.status_code == 200, f"Failed to login with existing user: {login_response.text}"
    else:
        # New user registration should succeed
        assert response.status_code == 201, f"Failed to register user: {response.text}"
    
    return test_user


@pytest_asyncio.fixture(scope="function")
async def user_token_headers(client: AsyncClient, registered_user: dict) -> dict:
    """
    Get token headers for registered user.
    """
    login_data = {
        "username": registered_user["email"],
        "password": registered_user["password"],
    }
    response = await client.post("/auth/jwt/login", data=login_data)
    assert response.status_code == 200, f"Failed to login: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}