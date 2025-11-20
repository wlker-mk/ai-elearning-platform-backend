"""
Utilitaires pour l'envoi d'emails
Fichier: shared/shared/utils/email_utils.py
"""
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_verification_email(email: str, token: str) -> bool:
    """
    Envoyer un email de vérification
    
    Args:
        email: Email du destinataire
        token: Token de vérification
        
    Returns:
        True si envoyé avec succès, False sinon
    """
    try:
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        verification_url = f"{frontend_url}/verify-email?token={token}"
        
        subject = 'Verify your email - LMS Platform'
        message = f"""
        Welcome to LMS Platform!
        
        Please verify your email address by clicking the link below:
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you did not create an account, please ignore this email.
        
        Best regards,
        The LMS Team
        """
        
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4F46E5;">Welcome to LMS Platform!</h2>
                    <p>Thank you for creating an account. Please verify your email address to get started.</p>
                    <div style="margin: 30px 0;">
                        <a href="{verification_url}" 
                           style="background-color: #4F46E5; color: white; padding: 12px 30px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;">
                            Verify Email Address
                        </a>
                    </div>
                    <p style="color: #666; font-size: 14px;">
                        This link will expire in 24 hours. If you did not create an account, please ignore this email.
                    </p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="color: #999; font-size: 12px;">
                        Best regards,<br>
                        The LMS Team
                    </p>
                </div>
            </body>
        </html>
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {str(e)}")
        return False


def send_password_reset_email(email: str, token: str) -> bool:
    """
    Envoyer un email de réinitialisation de mot de passe
    
    Args:
        email: Email du destinataire
        token: Token de réinitialisation
        
    Returns:
        True si envoyé avec succès, False sinon
    """
    try:
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        reset_url = f"{frontend_url}/reset-password?token={token}"
        
        subject = 'Reset your password - LMS Platform'
        message = f"""
        Password Reset Request
        
        You have requested to reset your password. Click the link below to proceed:
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you did not request a password reset, please ignore this email and your password will remain unchanged.
        
        Best regards,
        The LMS Team
        """
        
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4F46E5;">Password Reset Request</h2>
                    <p>You have requested to reset your password. Click the button below to proceed:</p>
                    <div style="margin: 30px 0;">
                        <a href="{reset_url}" 
                           style="background-color: #4F46E5; color: white; padding: 12px 30px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;">
                            Reset Password
                        </a>
                    </div>
                    <p style="color: #666; font-size: 14px;">
                        This link will expire in 1 hour. If you did not request a password reset, 
                        please ignore this email and your password will remain unchanged.
                    </p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="color: #999; font-size: 12px;">
                        Best regards,<br>
                        The LMS Team
                    </p>
                </div>
            </body>
        </html>
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Password reset email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        return False


def send_mfa_enabled_notification(email: str) -> bool:
    """
    Envoyer une notification d'activation du MFA
    
    Args:
        email: Email du destinataire
        
    Returns:
        True si envoyé avec succès, False sinon
    """
    try:
        subject = 'Two-Factor Authentication Enabled - LMS Platform'
        message = """
        Two-Factor Authentication has been enabled on your account.
        
        Your account is now more secure. You will need to enter a verification code 
        from your authenticator app each time you log in.
        
        If you did not enable this feature, please contact our support team immediately.
        
        Best regards,
        The LMS Team
        """
        
        html_message = """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #10B981;">Two-Factor Authentication Enabled</h2>
                    <p>Two-Factor Authentication has been successfully enabled on your account.</p>
                    <p>Your account is now more secure. You will need to enter a verification code 
                       from your authenticator app each time you log in.</p>
                    <div style="background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0; color: #92400E;">
                            <strong>Security Notice:</strong> If you did not enable this feature, 
                            please contact our support team immediately.
                        </p>
                    </div>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="color: #999; font-size: 12px;">
                        Best regards,<br>
                        The LMS Team
                    </p>
                </div>
            </body>
        </html>
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"MFA enabled notification sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send MFA notification to {email}: {str(e)}")
        return False


def send_suspicious_login_alert(email: str, ip_address: str, location: str, device: str) -> bool:
    """
    Envoyer une alerte de connexion suspecte
    
    Args:
        email: Email du destinataire
        ip_address: Adresse IP de la connexion
        location: Localisation
        device: Appareil utilisé
        
    Returns:
        True si envoyé avec succès, False sinon
    """
    try:
        subject = 'Suspicious Login Alert - LMS Platform'
        message = f"""
        We detected a login to your account from a new device or location.
        
        Details:
        - IP Address: {ip_address}
        - Location: {location}
        - Device: {device}
        
        If this was you, you can safely ignore this email.
        
        If this wasn't you, please:
        1. Change your password immediately
        2. Review your account activity
        3. Enable two-factor authentication for added security
        
        Best regards,
        The LMS Team
        """
        
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background-color: #FEE2E2; border-left: 4px solid #EF4444; padding: 15px; margin-bottom: 20px;">
                        <h2 style="color: #991B1B; margin: 0;">Suspicious Login Alert</h2>
                    </div>
                    <p>We detected a login to your account from a new device or location.</p>
                    <div style="background-color: #F3F4F6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">Login Details:</h3>
                        <ul style="list-style: none; padding: 0;">
                            <li><strong>IP Address:</strong> {ip_address}</li>
                            <li><strong>Location:</strong> {location}</li>
                            <li><strong>Device:</strong> {device}</li>
                        </ul>
                    </div>
                    <p>If this was you, you can safely ignore this email.</p>
                    <p>If this wasn't you, please take the following actions immediately:</p>
                    <ol>
                        <li>Change your password</li>
                        <li>Review your account activity</li>
                        <li>Enable two-factor authentication for added security</li>
                    </ol>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="color: #999; font-size: 12px;">
                        Best regards,<br>
                        The LMS Team
                    </p>
                </div>
            </body>
        </html>
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Suspicious login alert sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send suspicious login alert to {email}: {str(e)}")
        return False