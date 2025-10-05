#!/usr/bin/env python3
"""
Script pour créer un utilisateur et obtenir un token d'authentification
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"

def create_user():
    """Créer un nouvel utilisateur."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }

    print("👤 Creating user...")
    response = requests.post(f"{BASE_URL}/users/", json=user_data)

    if response.status_code == 201:
        print("✅ User created successfully")
        return response.json()
    else:
        print(f"❌ Failed to create user: {response.status_code}")
        print(response.text)
        return None

def get_token():
    """Obtenir un token d'authentification."""
    token_data = {
        "username": "testuser",
        "password": "testpass123"
    }

    print("🔑 Getting authentication token...")
    response = requests.post(f"{BASE_URL}/token", data=token_data)

    if response.status_code == 200:
        token_info = response.json()
        print("✅ Token obtained successfully")
        print(f"🔑 Token: {token_info['access_token'][:50]}...")
        return token_info['access_token']
    else:
        print(f"❌ Failed to get token: {response.status_code}")
        print(response.text)
        return None

def test_email_endpoint(token):
    """Tester l'endpoint email avec le token."""
    email_data = {
        "to": "destination@example.com",
        "subject": "Test Email from API",
        "body": "Ceci est un email de test envoyé depuis l'API SkyPionners !"
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    print("📧 Testing email endpoint...")
    response = requests.post(f"{BASE_URL}/email/send", json=email_data, headers=headers)

    if response.status_code == 200:
        print("✅ Email sent successfully!")
        print(response.json())
    else:
        print(f"❌ Failed to send email: {response.status_code}")
        print(response.text)

def main():
    """Fonction principale."""
    print("🚀 Testing SkyPionners API Authentication & Email...")

    # Étape 1: Créer un utilisateur
    user = create_user()
    if not user:
        print("❌ Cannot continue without user creation")
        return

    # Étape 2: Obtenir le token
    token = get_token()
    if not token:
        print("❌ Cannot continue without token")
        return

    # Étape 3: Tester l'endpoint email
    test_email_endpoint(token)

    print("\n🎉 All tests completed!")
    print(f"\n💡 Vous pouvez maintenant utiliser ce token: {token[:50]}...")

if __name__ == "__main__":
    main()
