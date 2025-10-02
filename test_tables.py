#!/usr/bin/env python3
"""
Script de test de création des tables
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import Base

def test_table_creation():
    """Test de création des tables"""
    print("🔧 Test de création des tables...")

    # Configuration SQLite comme dans les tests
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

    try:
        # Créer les tables
        Base.metadata.create_all(bind=engine)
        print("✅ Tables créées avec succès!")

        # Vérifier qu'elles existent
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = result.fetchall()
            print(f"📋 Tables trouvées: {[table[0] for table in tables]}")

            # Vérifier la structure de la table users
            result = conn.execute(text("PRAGMA table_info(users);"))
            columns = result.fetchall()
            print(f"📊 Colonnes de 'users': {[col[1] for col in columns]}")

        return True

    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")
        return False

if __name__ == "__main__":
    success = test_table_creation()
    if success:
        print("\n🎉 Création des tables réussie!")
    else:
        print("\n⚠️ Problème avec la création des tables.")
