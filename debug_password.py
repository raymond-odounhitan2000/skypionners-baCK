#!/usr/bin/env python3
"""
Script de débogage détaillé pour tracer l'erreur bcrypt
"""

import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import Base

def debug_password_issue():
    """Debug password hashing issue"""
    print("🔍 Debug password hashing...")

    # Configuration identique aux tests
    SQLALCHEMY_DATABASE_URL = "sqlite:///./debug.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Créer les tables
    Base.metadata.create_all(bind=engine)

    try:
        # Test direct de get_password_hash
        from app.services.auth_service import get_password_hash

        test_password = "testpass123"
        print(f"📝 Testing password: '{test_password}'")
        print(f"📏 Password length: {len(test_password)} chars")
        print(f"📏 Password bytes: {len(test_password.encode('utf-8'))} bytes")

        hashed = get_password_hash(test_password)
        print(f"✅ Password hashed successfully: {hashed[:20]}...")

        # Test de création d'utilisateur
        db = TestingSessionLocal()
        try:
            from app.services.auth_service import create_user
            from app.schemas.user import UserCreate

            user_data = UserCreate(
                email="test@example.com",
                username="testuser",
                password=test_password,
                full_name="Test User"
            )

            print("👤 Creating user...")
            user = create_user(db, user_data)
            print(f"✅ User created: {user.username}")

        except Exception as e:
            print(f"❌ Error creating user: {e}")
            traceback.print_exc()
        finally:
            db.close()

    except Exception as e:
        print(f"❌ Error in password hashing: {e}")
        traceback.print_exc()

    # Nettoyer
    Base.metadata.drop_all(bind=engine)

if __name__ == "__main__":
    debug_password_issue()
