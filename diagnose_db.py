#!/usr/bin/env python3
"""
Script de diagnostic pour tester la connexion PostgreSQL
"""

import os
import sys
from sqlalchemy import create_engine, text

def test_postgresql_connection():
    """Test de connexion PostgreSQL avec différentes configurations"""

    # Test 1: Configuration actuelle
    print("🔍 Test 1: Configuration actuelle...")
    try:
        from app.core.config import settings
        print(f"📡 DATABASE_URL actuelle: {settings.DATABASE_URL}")

        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Connexion réussie avec configuration actuelle!")
            return True
    except Exception as e:
        print(f"❌ Échec avec configuration actuelle: {e}")

    # Test 2: Configuration locale par défaut
    print("\n🔍 Test 2: Configuration locale par défaut...")
    try:
        local_url = "postgresql://postgres:password@localhost:5432/test_db"
        print(f"📡 Test avec URL locale: {local_url}")

        engine = create_engine(local_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Connexion réussie avec configuration locale!")
            print("💡 Utilisez cette URL dans votre .env: postgresql://postgres:password@localhost:5432/test_db")
            return True
    except Exception as e:
        print(f"❌ Échec avec configuration locale: {e}")

    # Test 3: SQLite pour vérifier que SQLAlchemy fonctionne
    print("\n🔍 Test 3: Test avec SQLite...")
    try:
        sqlite_url = "sqlite:///./test.db"
        print(f"📡 Test avec SQLite: {sqlite_url}")

        engine = create_engine(sqlite_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ SQLite fonctionne correctement!")
            print("💡 Vous pouvez utiliser SQLite pour le développement: sqlite:///./skypionners.db")
    except Exception as e:
        print(f"❌ Même SQLite échoue: {e}")
        return False

    return False

if __name__ == "__main__":
    print("🔧 Diagnostic de connexion PostgreSQL")
    print("=" * 50)

    success = test_postgresql_connection()

    if success:
        print("\n🎉 Au moins une configuration fonctionne!")
    else:
        print("\n⚠️  Aucune configuration ne fonctionne.")
        print("📋 Vérifiez:")
        print("   1. Votre base PostgreSQL est démarrée")
        print("   2. Vos credentials sont corrects")
        print("   3. Le hostname/port sont accessibles")
        print("   4. Le firewall autorise la connexion")
