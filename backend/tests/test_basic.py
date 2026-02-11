# tests/test_basic.py
import pytest
import sys
import os

# Path'i ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.asyncio
async def test_health_check(async_client):
    """Test health endpoint"""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ Health check passed")


@pytest.mark.asyncio
async def test_root_endpoint(async_client):
    """Test root endpoint"""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "PDF AI" in data["message"]
    print("✅ Root endpoint passed")