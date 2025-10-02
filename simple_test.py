#!/usr/bin/env python3
"""
Test simple de l'API OAuth2
"""

import requests

BASE_URL = "http://localhost:8000"

def test_api():
    print("🔐 Testing Simple OAuth2 API Demo...")

    # 1. Health check
    print("\n💚 Health check:")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ {response.json()}")

    # 2. Create user
    print("\n👤 Create user:")
    user_data = {
        "username": "demo_user",
        "email": "demo@example.com",
        "password": "demo123",
        "full_name": "Demo User"
    }
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ {response.json()}")

    # 3. Login
    print("\n🔑 Login:")
    response = requests.post(f"{BASE_URL}/login?username=demo_user&password=demo123")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        login_data = response.json()
        print(f"   ✅ Token: {login_data['access_token'][:20]}...")
        print(f"   ✅ User: {login_data['user']['username']}")

    # 4. Access protected data
    print("\n🔒 Access protected endpoint:")
    headers = {"Authorization": "Bearer demo-jwt-token-12345"}
    response = requests.get(f"{BASE_URL}/protected", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ {data['message']}")
        print(f"   ✅ Secret: {data['data']['secret']}")

    # 5. Interactive docs
    print("\n📚 Interactive Documentation:")
    print(f"   📖 Swagger UI: {BASE_URL}/docs")
    print(f"   📋 ReDoc: {BASE_URL}/redoc")

    print("\n🎉 API Demo completed successfully!")

if __name__ == "__main__":
    test_api()
