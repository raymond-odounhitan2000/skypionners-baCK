from typing import List, Optional
from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):
    """Schéma de base pour un email."""
    to: EmailStr
    subject: str
    body: str
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None


class EmailTemplate(BaseModel):
    """Schéma pour un template d'email."""
    name: str
    subject: str
    html_body: str
    text_body: Optional[str] = None


class EmailResponse(BaseModel):
    """Réponse après envoi d'email."""
    message_id: str
    success: bool
    message: str


class EmailVerification(BaseModel):
    """Schéma pour la vérification d'email."""
    email: EmailStr
    verification_token: str


class PasswordReset(BaseModel):
    """Schéma pour la réinitialisation de mot de passe."""
    email: EmailStr
    reset_token: str
