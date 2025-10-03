from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings

# Configuration MINIMALE - seulement les paramètres essentiels
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_TLS,
    MAIL_SSL_TLS=settings.MAIL_SSL,
    USE_CREDENTIALS=True
)

fm = FastMail(conf)

async def send_email(recipients, subject, body, html_body=None):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        html=html_body or body,
        subtype='html' if html_body else 'plain'
    )

    await fm.send_message(message)
    return {"message": "Email sent successfully"}

async def send_verification_email(email: str, verification_token: str):
    """Envoyer un email de vérification."""
    subject = "Vérification de votre compte SkyPionners"
    body = f"""Bonjour,
        Pour vérifier votre compte, cliquez sur le lien suivant :
        http://localhost:8000/verify?token={verification_token}
        Ce lien expirera dans 24 heures.
        Cordialement,
        L'équipe SkyPionners
    """
    
    await send_email([email], subject, body)
    return {"message": "Email de vérification envoyé"}

async def send_password_reset_email(email: str, reset_token: str):
    """Envoyer un email de réinitialisation de mot de passe."""
    subject = "Réinitialisation de votre mot de passe SkyPionners"
    body = f"""Bonjour,
        Vous avez demandé à réinitialiser votre mot de passe.
        Cliquez sur le lien suivant pour définir un nouveau mot de passe :
        http://localhost:8000/reset-password?token={reset_token}
        Ce lien expirera dans 1 heure.
        Cordialement,
        L'équipe SkyPionners
    """
    
    await send_email([email], subject, body)
    return {"message": "Email de réinitialisation envoyé"}

async def send_welcome_email(email: str, username: str):
    """Envoyer un email de bienvenue."""
    subject = "Bienvenue chez SkyPionners !"
    body = f"""Bonjour {username},
        Bienvenue chez SkyPionners ! Votre compte a été créé avec succès.
        Vous pouvez maintenant accéder à toutes les fonctionnalités de notre plateforme.

        Cordialement,
        L'équipe SkyPionners
    """
    
    await send_email([email], subject, body)
    return {"message": "Email de bienvenue envoyé"}