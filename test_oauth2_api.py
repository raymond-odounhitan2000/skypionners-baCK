#!/usr/bin/env python3
"""
Script de test de l'API OAuth2 complète
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_oauth2_flow():
    """Test the complete OAuth2 flow"""
    print("🔐 Testing OAuth2 API...")

    # 1. Create a test user first
    print("\n📝 Step 1: Create test user")
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User"
    }

    response = requests.post(f"{BASE_URL}/api/v1/users/", json=user_data)
    if response.status_code == 201:
        print("✅ User created successfully")
    else:
        print(f"❌ Failed to create user: {response.status_code} - {response.text}")

    # 2. Test login with /token endpoint
    print("\n🔑 Step 2: Test OAuth2 token endpoint")
    token_data = {
        "username": "testuser",
        "password": "testpass123"
    }

    response = requests.post(f"{BASE_URL}/token", data=token_data)
    if response.status_code == 200:
        token_response = response.json()
        print("✅ Token obtained successfully")
        print(f"   Token type: {token_response['token_type']}")
        print(f"   Access token: {token_response['access_token'][:20]}...")
        access_token = token_response['access_token']
    else:
        print(f"❌ Failed to get token: {response.status_code} - {response.text}")
        return False

    # 3. Test protected endpoint with token
    print("\n🔒 Step 3: Test protected endpoint")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        print("✅ Protected endpoint accessed successfully")
        print(f"   Current user: {user_info['username']}")
    else:
        print(f"❌ Failed to access protected endpoint: {response.status_code} - {response.text}")

    # 4. Test alternative login endpoint
    print("\n🔑 Step 4: Test alternative login endpoint")
    login_response = requests.post(f"{BASE_URL}/login",
                                 json={"username": "testuser", "password": "testpass123"})
    if login_response.status_code == 200:
        login_data = login_response.json()
        print("✅ Alternative login successful")
        print(f"   User info: {login_data['user']['username']}")
    else:
        print(f"❌ Alternative login failed: {login_response.status_code} - {login_response.text}")

    # 5. Test health endpoints (should work without auth)
    print("\n💚 Step 5: Test health endpoints")
    health_response = requests.get(f"{BASE_URL}/api/v1/health/")
    if health_response.status_code == 200:
        print("✅ Health endpoint accessible")
    else:
        print(f"❌ Health endpoint failed: {health_response.status_code}")

    print("\n🎉 OAuth2 API test completed!")
    return True

if __name__ == "__main__":
    test_oauth2_flow()
