#!/usr/bin/env python3
"""
Script de test pour le service d'email
"""

import asyncio
import requests
from app.services.email_service import send_welcome_email, send_verification_email

async def test_email_service():
    """Tester le service d'email."""
    print("📧 Testing Email Service...")

    try:
        # Test 1: Email de bienvenue
        print("\n🎉 Test 1: Welcome Email")
        await send_welcome_email("test@example.com", "TestUser")
        print("✅ Welcome email sent successfully")

        # Test 2: Email de vérification
        print("\n🔐 Test 2: Verification Email")
        await send_verification_email("test@example.com", "test-token-123")
        print("✅ Verification email sent successfully")

        print("\n🎉 Email service tests completed successfully!")

    except Exception as e:
        print(f"❌ Email service test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_email_service())
