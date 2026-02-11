# tests/integration/test_auth.py
import pytest
import httpx


@pytest.mark.asyncio
async def test_health_check(async_client):
    """Test health check endpoint"""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_user(async_client, test_user_data):
    """Test user registration"""
    response = await async_client.post("/api/auth/register", json=test_user_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]
    assert "id" in data
    assert "created_at" in data
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_register_duplicate_user(async_client, test_user_data):
    """Test duplicate user registration"""
    # First registration
    response1 = await async_client.post("/api/auth/register", json=test_user_data)
    assert response1.status_code == 200
    
    # Second registration with same data
    response2 = await async_client.post("/api/auth/register", json=test_user_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(async_client, test_user_data):
    """Test successful login"""
    # First register
    await async_client.post("/api/auth/register", json=test_user_data)
    
    # Then login
    response = await async_client.post("/api/auth/login", data={
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 50  # Token uzunluğu


@pytest.mark.asyncio
async def test_login_wrong_password(async_client, test_user_data):
    """Test login with wrong password"""
    # Register user
    await async_client.post("/api/auth/register", json=test_user_data)
    
    # Login with wrong password
    response = await async_client.post("/api/auth/login", data={
        "username": test_user_data["username"],
        "password": "WrongPassword123!"
    })
    
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_current_user(authenticated_client, test_user_data):
    """Test getting current user info"""
    response = await authenticated_client.get("/api/auth/me")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]
    assert "id" in data


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(async_client):
    """Test getting user info without token"""
    response = await async_client.get("/api/auth/me")
    
    assert response.status_code == 401
    assert "credentials" in response.json()["detail"].lower()