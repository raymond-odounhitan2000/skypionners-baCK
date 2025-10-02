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
        print(f"📝 Original password: '{test_password}'")
        print(f"📏 Original length: {len(test_password)} chars")
        print(f"📏 Original bytes: {len(test_password.encode('utf-8'))} bytes")
        print(f"🔍 Type: {type(test_password)}")

        # Test the function step by step
        password = test_password
        print(f"📝 Password before truncation check: '{password}'")

        if len(password.encode('utf-8')) > 72:
            password = password[:72]
            print(f"📝 Password after truncation: '{password}'")
            print(f"📏 Truncated length: {len(password)} chars")
            print(f"📏 Truncated bytes: {len(password.encode('utf-8'))} bytes")

        print(f"📝 Final password for hashing: '{password}'")

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
            print(f"📝 User password: '{user_data.password}'")
            print(f"📏 User password length: {len(user_data.password)} chars")
            print(f"📏 User password bytes: {len(user_data.password.encode('utf-8'))} bytes")

            user = create_user(db, user_data)
            print(f"✅ User created: {user.username}")

        except Exception as e:
            print(f"❌ Error creating user: {e}")
            print(f"❌ Error type: {type(e)}")
            traceback.print_exc()
        finally:
            db.close()

    except Exception as e:
        print(f"❌ Error in password hashing: {e}")
        print(f"❌ Error type: {type(e)}")
        traceback.print_exc()

    # Nettoyer
    Base.metadata.drop_all(bind=engine)

if __name__ == "__main__":
    debug_password_issue()
