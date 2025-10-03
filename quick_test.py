#!/usr/bin/env python3
"""
Test rapide de l'API SkyPionners
"""

import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_api():
    """Test rapide de l'API."""
    print("🚀 Test Rapide API SkyPionners")

    # Créer utilisateur unique
    unique_id = str(int(time.time()))[-6:]
    username = f"test_{unique_id}"

    user_data = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "testpass123",
        "full_name": f"Test User {unique_id}"
    }

    print(f"👤 Création utilisateur: {username}")

    # Créer utilisateur
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    print(f"Status création: {response.status_code}")

    if response.status_code != 201:
        print(f"❌ Échec: {response.text}")
        return

    # Obtenir token
    token_response = requests.post(f"{BASE_URL}/token", data={
        "username": username,
        "password": "testpass123"
    })

    print(f"Status token: {token_response.status_code}")

    if token_response.status_code != 200:
        print(f"❌ Échec token: {token_response.text}")
        return

    token = token_response.json()["access_token"]

    # Tester email
    email_response = requests.post(f"{BASE_URL}/email/send",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "to": "raymond01.dev@gmail.com",
            "subject": "Test API",
            "body": "Test email"
        }
    )

    print(f"Status email: {email_response.status_code}")

    if email_response.status_code == 200:
        print("✅ Email envoyé avec succès !")
        print(f"📧 Réponse: {email_response.json()}")
    else:
        print(f"❌ Échec email: {email_response.text}")

if __name__ == "__main__":
    test_api()
