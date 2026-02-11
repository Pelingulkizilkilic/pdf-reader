# smoke_test.py
"""
Simple smoke test script - Run this first!
"""
import requests
import time
import sys

def run_smoke_tests():
    """Run basic smoke tests on the running API"""
    
    BASE_URL = 'http://localhost:8000'
    
    print('🚀 PDF AI Backend Smoke Tests')
    print('=' * 50)
    
    tests = []
    
    # Test 1: Server is running
    print('\n1. Testing server connection...')
    try:
        resp = requests.get(f'{BASE_URL}/health', timeout=5)
        if resp.status_code == 200:
            print(f'   ✅ Server is running (status: {resp.status_code})')
            tests.append(('Server Running', True))
        else:
            print(f'   ❌ Server returned status: {resp.status_code}')
            tests.append(('Server Running', False))
    except requests.exceptions.ConnectionError:
        print('   ❌ Cannot connect to server')
        print('   💡 Make sure server is running:')
        print('      uvicorn app.main:app --reload --host 0.0.0.0 --port 8000')
        tests.append(('Server Running', False))
        return tests
    
    # Test 2: Health endpoint
    print('\n2. Testing health endpoint...')
    try:
        resp = requests.get(f'{BASE_URL}/health', timeout=3)
        data = resp.json()
        if data.get('status') == 'healthy':
            print('   ✅ Health endpoint working')
            tests.append(('Health Endpoint', True))
        else:
            print(f'   ❌ Health endpoint error: {data}')
            tests.append(('Health Endpoint', False))
    except Exception as e:
        print(f'   ❌ Health test failed: {e}')
        tests.append(('Health Endpoint', False))
    
    # Test 3: Root endpoint
    print('\n3. Testing root endpoint...')
    try:
        resp = requests.get(f'{BASE_URL}/', timeout=3)
        if resp.status_code == 200:
            print('   ✅ Root endpoint working')
            tests.append(('Root Endpoint', True))
        else:
            print(f'   ❌ Root endpoint status: {resp.status_code}')
            tests.append(('Root Endpoint', False))
    except Exception as e:
        print(f'   ❌ Root endpoint failed: {e}')
        tests.append(('Root Endpoint', False))
    
    # Test 4: API Documentation
    print('\n4. Testing API documentation...')
    try:
        resp = requests.get(f'{BASE_URL}/docs', timeout=3, allow_redirects=True)
        if resp.status_code in [200, 307]:
            print('   ✅ API docs available')
            tests.append(('API Documentation', True))
        else:
            print(f'   ❌ API docs status: {resp.status_code}')
            tests.append(('API Documentation', False))
    except Exception as e:
        print(f'   ❌ API docs failed: {e}')
        tests.append(('API Documentation', False))
    
    # Test 5: Test with existing user (pln)
    print('\n5. Testing authentication...')
    try:
        resp = requests.post(
            f'{BASE_URL}/api/auth/login',
            data={'username': 'pln', 'password': 'test123'},
            timeout=5
        )
        
        if resp.status_code == 200:
            token = resp.json().get('access_token', '')
            print('   ✅ Login successful with test user')
            print(f'   🔑 Token received: {token[:20]}...')
            tests.append(('Authentication', True))
            
            # Test 6: Protected endpoint with token
            print('\n6. Testing protected endpoint...')
            headers = {'Authorization': f'Bearer {token}'}
            resp = requests.get(f'{BASE_URL}/api/auth/me', headers=headers, timeout=5)
            
            if resp.status_code == 200:
                user_data = resp.json()
                print(f'   ✅ User info retrieved')
                print(f'   👤 Username: {user_data.get("username")}')
                print(f'   📧 Email: {user_data.get("email")}')
                tests.append(('Protected Endpoint', True))
            else:
                print(f'   ❌ User info failed: {resp.status_code}')
                tests.append(('Protected Endpoint', False))
                
        elif resp.status_code == 401:
            print('   ⚠️  Login failed (wrong credentials)')
            print('   💡 Try registering first or check password')
            tests.append(('Authentication', False))
        else:
            print(f'   ❌ Login unexpected status: {resp.status_code}')
            tests.append(('Authentication', False))
            
    except Exception as e:
        print(f'   ❌ Auth test failed: {e}')
        tests.append(('Authentication', False))
    
    return tests


def main():
    """Main function"""
    print('Starting smoke tests in 2 seconds...')
    time.sleep(2)
    
    tests = run_smoke_tests()
    
    print('\n' + '=' * 50)
    print('📊 TEST RESULTS:')
    print('=' * 50)
    
    passed = 0
    failed = 0
    
    for test_name, success in tests:
        status = '✅ PASS' if success else '❌ FAIL'
        print(f'{status} - {test_name}')
        if success:
            passed += 1
        else:
            failed += 1
    
    print('\n' + '=' * 50)
    print(f'Total: {len(tests)} tests')
    print(f'Passed: {passed}')
    print(f'Failed: {failed}')
    
    if failed == 0:
        print('\n🎉 ALL TESTS PASSED!')
        return 0
    else:
        print('\n⚠️  SOME TESTS FAILED')
        return 1


if __name__ == '__main__':
    sys.exit(main())