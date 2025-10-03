from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, EmailStr
import asyncio
import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.email_service import (
    send_welcome_email,
    send_verification_email,
    send_password_reset_email,
    send_email
)

router = APIRouter()

class EmailTest(BaseModel):
    email: EmailStr
    username: str = "Test User"

class VerificationRequest(BaseModel):
    email: EmailStr

class PasswordResetRequest(BaseModel):
    email: EmailStr

@router.post("/test-welcome", status_code=status.HTTP_200_OK)
async def test_welcome_email(email_data: EmailTest):
    """Test d envoi d email de bienvenue."""
    try:
        result = await send_welcome_email(
            email=email_data.email,
            username=email_data.username
        )
        return {
            "message": "Email de bienvenue envoyé avec succès",
            "recipient": email_data.email,
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l envoi d email: {str(e)}"
        )

@router.post("/test-verification", status_code=status.HTTP_200_OK)
async def test_verification_email_endpoint(email_data: EmailTest):
    """Test d envoi d email de vérification."""
    try:
        result = await send_verification_email(
            email=email_data.email,
            verification_token="test_token_123"
        )
        return {
            "message": "Email de vérification envoyé avec succès",
            "recipient": email_data.email,
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l envoi d email: {str(e)}"
        )

@router.post("/test-reset-password", status_code=status.HTTP_200_OK)
async def test_password_reset_email_endpoint(email_data: EmailTest):
    """Test d envoi d email de réinitialisation."""
    try:
        result = await send_password_reset_email(
            email=email_data.email,
            reset_token="test_reset_token_456"
        )
        return {
            "message": "Email de réinitialisation envoyé avec succès",
            "recipient": email_data.email,
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l envoi d email: {str(e)}"
        )

@router.get("/templates")
async def list_email_templates():
    """Lister les templates d email disponibles."""
    try:
        template_dir = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "templates", "email"
        )

        if os.path.exists(template_dir):
            templates = [f for f in os.listdir(template_dir) if f.endswith('.html')]
            return {
                "templates": templates,
                "count": len(templates),
                "directory": template_dir
            }
        else:
            return {"error": "Dossier templates non trouvé"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la lecture des templates: {str(e)}"
        )

@router.post("/send-welcome/{user_id}", status_code=status.HTTP_200_OK)
async def send_welcome_email_endpoint(user_id: int, background_tasks: BackgroundTasks):
    """Envoyer un email de bienvenue à un utilisateur spécifique."""
    try:
        # Ici vous pourriez récupérer l utilisateur depuis la DB
        # Pour l instant, simulation
        result = await send_welcome_email(
            email=f"user{user_id}@example.com",
            username=f"User {user_id}"
        )
        return {
            "message": f"Email de bienvenue envoyé à l utilisateur {user_id}",
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l envoi d email: {str(e)}"
        )
