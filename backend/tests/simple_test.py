# tests/simple_test.py
import sys
import os

# Python path'ine app modülünü ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

def test_auth_manual():
    """Manuel auth test - pytest olmadan"""
    print("🚀 Running manual auth test...")
    
    BASE_URL = "http://localhost:8000"
    
    try:
        # 1. Test health endpoint
        print("1. Testing health endpoint...")
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
        
        # 2. Test auth test endpoint
        print("\n2. Testing auth test endpoint...")
        resp = requests.get(f"{BASE_URL}/api/auth/test", timeout=5)
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
        
        # 3. Try login with existing user
        print("\n3. Testing login with 'pln' user...")
        resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            data={"username": "pln", "password": "test123"},
            timeout=5
        )
        
        if resp.status_code == 200:
            token = resp.json()["access_token"]
            print(f"   ✅ Login successful!")
            print(f"   Token (first 20 chars): {token[:20]}...")
            
            # 4. Test /me endpoint
            print("\n4. Testing /me endpoint...")
            headers = {"Authorization": f"Bearer {token}"}
            resp = requests.get(f"{BASE_URL}/api/auth/me", headers=headers, timeout=5)
            print(f"   Status: {resp.status_code}")
            if resp.status_code == 200:
                user_data = resp.json()
                print(f"   User: {user_data['username']}")
                print(f"   Email: {user_data['email']}")
                print("   ✅ All tests passed!")
                return True
            else:
                print(f"   ❌ /me failed: {resp.json()}")
                return False
        else:
            print(f"   ❌ Login failed: {resp.status_code}")
            print(f"   Response: {resp.json()}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("   Run: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_auth_manual()
    sys.exit(0 if success else 1)