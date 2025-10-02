#!/usr/bin/env python3
"""
Script de débogage des imports
"""

def test_imports():
    """Test if all imports work correctly"""
    print("🔍 Testing imports...")

    try:
        print("📦 Testing core.database import...")
        from app.core.database import get_db
        print("✅ get_db imported successfully")

        print("📦 Testing models.user import...")
        from app.models.user import Base
        print("✅ Base imported successfully")

        print("📦 Testing services.auth_service import...")
        from app.services.auth_service import create_user, get_current_active_user
        print("✅ auth_service functions imported successfully")

        print("📦 Testing schemas import...")
        from app.schemas.user import UserCreate
        print("✅ schemas imported successfully")

        print("\n🎉 All imports work correctly!")
        return True

    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()
