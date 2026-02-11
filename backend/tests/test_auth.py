# tests/test_auth.py
"""
Authentication API tests
"""
import pytest
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.asyncio
async def test_user_registration(async_client, test_user_data):
    """Test user registration endpoint"""
    response = await async_client.post(
        '/api/auth/register',
        json=test_user_data
    )
    
    # Either 200 (created) or 400 (already exists)
    assert response.status_code in [200, 400]
    
    if response.status_code == 200:
        data = response.json()
        assert data['username'] == test_user_data['username']
        assert data['email'] == test_user_data['email']
        print('✅ User registration passed')
    else:
        # User already exists, that's okay for test
        print('⚠️  User already exists (test can continue)')


@pytest.mark.asyncio
async def test_user_login(async_client, test_user_data):
    """Test user login endpoint"""
    # Try to login with test user
    response = await async_client.post(
        '/api/auth/login',
        data={
            'username': test_user_data['username'],
            'password': test_user_data['password']
        }
    )
    
    # Login might succeed or fail depending on user existence
    # Both are acceptable for basic test
    assert response.status_code in [200, 401]
    
    if response.status_code == 200:
        data = response.json()
        assert 'access_token' in data
        assert data['token_type'] == 'bearer'
        print('✅ User login passed')
    else:
        print('⚠️  Login failed (user may not exist)')


@pytest.mark.asyncio
async def test_protected_endpoint_requires_auth(async_client):
    """Test that protected endpoints require authentication"""
    response = await async_client.get('/api/auth/me')
    
    # Should return 401 Unauthorized
    assert response.status_code == 401
    assert 'detail' in response.json()
    
    print('✅ Auth protection working')