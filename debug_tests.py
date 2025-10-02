#!/usr/bin/env python3
"""
Script de débogage des fixtures de test
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import Base

def debug_test_setup():
    """Debug test database setup"""
    print("🔧 Debug test database setup...")

    # Configuration identique aux tests
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    try:
        print("📋 Before creating tables:")
        print(f"   Tables in metadata: {[table.name for table in Base.metadata.tables.values()]}")

        # Créer les tables (comme dans la fixture)
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")

        # Vérifier les tables créées
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = result.fetchall()
            print(f"📋 SQLite tables: {[table[0] for table in tables]}")

        # Tester une session
        db = TestingSessionLocal()
        try:
            # Essayer d'insérer un utilisateur de test
            from app.services.auth_service import create_user
            from app.schemas.user import UserCreate

            user_data = UserCreate(
                email="test@example.com",
                username="testuser",
                password="testpass123",
                full_name="Test User"
            )

            user = create_user(db, user_data)
            print(f"✅ User created: {user.username}")

            # Compter les utilisateurs
            from app.services.auth_service import get_users
            users = get_users(db)
            print(f"✅ Users count: {len(users)}")

        finally:
            db.close()

        # Nettoyer
        Base.metadata.drop_all(bind=engine)
        print("✅ Tables dropped successfully")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_test_setup()
    if success:
        print("\n🎉 Test setup works correctly!")
    else:
        print("\n⚠️ Test setup has issues.")
