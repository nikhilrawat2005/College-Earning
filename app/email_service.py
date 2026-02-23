from flask_mail import Message
from flask import current_app
from app.extensions import mail
import logging

logger = logging.getLogger(__name__)


class EmailService:

    @staticmethod
    def send_verification_email(email, username, code):
        try:
            msg = Message(
                subject="College Earning — Email Verification Code",
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[email],
                html=f"""
                <h2>College Earning Email Verification</h2>
                <p>Hi {username},</p>
                <p>Your verification code is: <strong>{code}</strong></p>
                <p>This code will expire in 10 minutes.</p>
                """
            )
            msg.body = f"Hi {username},\n\nYour verification code is: {code}\n\nThis code will expire in 10 minutes."

            mail.send(msg)
            logger.info(f"Verification email sent to {email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send verification email to {email}: {e}")
            return False

    @staticmethod
    def send_welcome_email(email, username):
        try:
            msg = Message(
                subject="Welcome to College Earning!",
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[email],
                html=f"""
                <h2>Welcome to College Earning 🎉</h2>
                <p>Hi {username},</p>
                <p>Your account has been successfully verified.</p>
                <p>We're excited to have you onboard!</p>
                """
            )
            msg.body = f"Hi {username},\n\nWelcome to College Earning! Your account is now verified."

            mail.send(msg)
            logger.info(f"Welcome email sent to {email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send welcome email to {email}: {e}")
            return False