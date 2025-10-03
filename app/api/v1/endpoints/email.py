from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.schemas.email import EmailSchema, EmailResponse, EmailVerification, PasswordReset
from app.services.email_service import (
    send_email,
    send_verification_email,
    send_password_reset_email,
    send_welcome_email
)
from app.services.auth_service import get_current_active_user
from app.core.database import get_db
from app.models.user import User

router = APIRouter()


@router.post("/send", response_model=EmailResponse)
async def send_custom_email(
    email_data: EmailSchema,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Envoyer un email personnalisé."""
    try:
        # Préparer les destinataires
        recipients = [email_data.to]
        if email_data.cc:
            recipients.extend(email_data.cc)
        if email_data.bcc:
            recipients.extend(email_data.bcc)

        # Envoyer en arrière-plan
        background_tasks.add_task(
            send_email,
            recipients,
            email_data.subject,
            email_data.body
        )

        return EmailResponse(
            message_id="email_queued",
            success=True,
            message="Email queued for sending"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )


@router.post("/verification")
async def send_verification(
    verification_data: EmailVerification,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Envoyer un email de vérification."""
    try:
        # Vérifier si l'utilisateur existe
        user = db.query(User).filter(User.email == verification_data.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Envoyer l'email en arrière-plan
        background_tasks.add_task(
            send_verification_email,
            verification_data.email,
            verification_data.verification_token
        )

        return {"message": "Verification email sent successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification email: {str(e)}"
        )


@router.post("/password-reset")
async def send_password_reset(
    reset_data: PasswordReset,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Envoyer un email de réinitialisation de mot de passe."""
    try:
        # Vérifier si l'utilisateur existe
        user = db.query(User).filter(User.email == reset_data.email).first()
        if not user:
            # Ne pas révéler si l'email existe ou non pour des raisons de sécurité
            return {"message": "If the email exists, a reset link has been sent"}

        # Envoyer l'email en arrière-plan
        background_tasks.add_task(
            send_password_reset_email,
            reset_data.email,
            reset_data.reset_token
        )

        return {"message": "Password reset email sent successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send password reset email: {str(e)}"
        )


@router.post("/welcome/{user_id}")
async def send_welcome(
    user_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Envoyer un email de bienvenue à un utilisateur."""
    try:
        # Vérifier que l'utilisateur actuel est admin ou que c'est son propre compte
        if not current_user.is_superuser and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        # Récupérer l'utilisateur destinataire
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Envoyer l'email en arrière-plan
        background_tasks.add_task(
            send_welcome_email,
            target_user.email,
            target_user.username
        )

        return {"message": "Welcome email sent successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send welcome email: {str(e)}"
        )
