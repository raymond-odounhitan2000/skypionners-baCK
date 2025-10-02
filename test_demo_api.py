#!/usr/bin/env python3
"""
Script de test de l'API OAuth2 de démonstration
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_oauth2_demo():
    """Test the OAuth2 demo API"""
    print("🔐 Testing OAuth2 Demo API...")

    # 1. Test health endpoint (no auth required)
    print("\n💚 Step 1: Health check")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✅ Health check successful")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return

    # 2. Create a test user
    print("\n👤 Step 2: Create test user")
    user_data = {
        "username": "testuser2",  # Changed username to avoid conflict
        "email": "test2@example.com",
        "password": "testpass123",
        "full_name": "Test User 2"
    }

    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    if response.status_code == 201:
        print("✅ User created successfully")
        user = response.json()
        print(f"   User: {user['username']} - {user['email']}")
    else:
        print(f"❌ User creation failed: {response.status_code} - {response.text}")

    # 3. Test login to get token
    print("\n🔑 Step 3: Get access token")
    # Use form data for OAuth2 endpoint
    token_response = requests.post(f"{BASE_URL}/token",
                                 data={"username": "testuser2", "password": "testpass123"})
    if token_response.status_code == 200:
        token_data = token_response.json()
        print("✅ Token obtained successfully")
        print(f"   Token type: {token_data['token_type']}")
        print(f"   Access token: {token_data['access_token']}")
        access_token = token_data['access_token']
    else:
        print(f"❌ Token request failed: {token_response.status_code} - {token_response.text}")
        return

    # 4. Test protected endpoint
    print("\n🔒 Step 4: Access protected endpoint")
    headers = {"Authorization": f"Bearer {access_token}"}

    protected_response = requests.get(f"{BASE_URL}/protected", headers=headers)
    if protected_response.status_code == 200:
        protected_data = protected_response.json()
        print("✅ Protected endpoint accessed successfully")
        print(f"   Message: {protected_data['message']}")
        print(f"   Secret data: {protected_data['data']}")
    else:
        print(f"❌ Protected endpoint failed: {protected_response.status_code} - {protected_response.text}")

    # 5. Test getting user info
    print("\n👤 Step 5: Get user information")
    user_response = requests.get(f"{BASE_URL}/users/testuser2")
    if user_response.status_code == 200:
        user_info = user_response.json()
        print("✅ User info retrieved successfully")
        print(f"   Username: {user_info['username']}")
        print(f"   Email: {user_info['email']}")
    else:
        print(f"❌ User info failed: {user_response.status_code} - {user_response.text}")

    print("\n🎉 OAuth2 Demo API test completed successfully!")
    print("\n📚 You can also test interactively at:")
    print(f"   📖 Swagger UI: {BASE_URL}/docs")
    print(f"   📋 ReDoc: {BASE_URL}/redoc")

if __name__ == "__main__":
    test_oauth2_demo()
