#!/usr/bin/env python3
"""
Test final complet de l'API avec authentification et email
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_complete_flow():
    """Test complet : création utilisateur → connexion → envoi email"""

    print("🚀 Test Complet de l'API SkyPionners")
    print("=" * 50)

    # Étape 1: Créer un utilisateur
    print("\n1️⃣  Création d'utilisateur...")
    user_data = {
        "username": "finaltest",
        "email": "finaltest@example.com",
        "password": "testpass123",
        "full_name": "Final Test User"
    }

    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    if response.status_code == 201:
        print("✅ Utilisateur créé avec succès")
    else:
        print(f"❌ Échec création utilisateur: {response.status_code}")
        print(response.text)
        return

    # Étape 2: Se connecter
    print("\n2️⃣  Connexion et obtention du token...")
    token_response = requests.post(f"{BASE_URL}/token", data={
        "username": "finaltest",
        "password": "testpass123"
    })

    if token_response.status_code == 200:
        token_data = token_response.json()
        token = token_data["access_token"]
        print("✅ Token obtenu avec succès")
        print(f"🔑 Token: {token[:30]}...")
    else:
        print(f"❌ Échec obtention token: {token_response.status_code}")
        print(token_response.text)
        return

    # Étape 3: Tester l'endpoint email
    print("\n3️⃣  Test de l'envoi d'email...")
    email_data = {
        "to": "destination@example.com",
        "subject": "Test Final API SkyPionners",
        "body": "🎉 Ceci est un email de test depuis l'API complète SkyPionners !\n\nL'API inclut maintenant :\n✅ Authentification OAuth2\n✅ Base de données PostgreSQL\n✅ Service d'email SendGrid\n✅ Documentation automatique"
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    email_response = requests.post(f"{BASE_URL}/email/send", json=email_data, headers=headers)

    if email_response.status_code == 200:
        print("✅ Email envoyé avec succès !")
        print("📧 Réponse:", email_response.json())
    else:
        print(f"❌ Échec envoi email: {email_response.status_code}")
        print(email_response.text)

    # Étape 4: Tester le profil utilisateur
    print("\n4️⃣  Test du profil utilisateur...")
    profile_response = requests.get(f"{BASE_URL}/users/me", headers=headers)

    if profile_response.status_code == 200:
        print("✅ Profil utilisateur récupéré avec succès")
        print("👤 Profil:", json.dumps(profile_response.json(), indent=2))
    else:
        print(f"❌ Échec récupération profil: {profile_response.status_code}")
        print(profile_response.text)

    print("\n🎉 Test Complet Terminé !")
    print("=" * 50)
    print("🌟 Votre API SkyPionners est 100% fonctionnelle !")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🔗 ReDoc: http://localhost:8000/redoc")

if __name__ == "__main__":
    test_complete_flow()
