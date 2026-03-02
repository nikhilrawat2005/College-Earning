from flask_mail import Message
from flask import current_app
from app.extensions import mail
import logging
import threading

logger = logging.getLogger(__name__)


class EmailService:

    @staticmethod
    def _send_email_async(app, msg):
        with app.app_context():
            try:
                mail.send(msg)
                logger.info(f"Email sent to {msg.recipients}")
            except Exception as e:
                logger.error(f"Failed to send email: {e}")

    @staticmethod
    def send_verification_email(email, username, code):
        """Synchronous version – raises exception on failure."""
        msg = Message(
            subject="Verify your Aaj Ka Freelancer Account",
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email],
        )
        msg.html = f"""
        <h2 style="color: #000; font-family: 'Fredoka', sans-serif;">Verify your Aaj Ka Freelancer Account</h2>
        <p>Hi {username},</p>
        <p>Welcome to Aaj Ka Freelancer! Use the verification code below to complete your signup:</p>
        <p style="font-size: 2rem; font-weight: bold; background: #f0f0f0; padding: 10px; display: inline-block;">{code}</p>
        <p>This code will expire in 10 minutes.</p>
        <p>If you didn't request this, please ignore this email.</p>
        <p style="margin-top: 30px;">— The Aaj Ka Freelancer Team</p>
        """
        msg.body = f"Hi {username},\n\nYour verification code is: {code}\n\nThis code will expire in 10 minutes."
        mail.send(msg)

    @staticmethod
    def send_verification_email_async(email, username, code):
        try:
            msg = Message(
                subject="Verify your Aaj Ka Freelancer Account",
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[email],
            )
            msg.html = f"""
            <h2 style="color: #000; font-family: 'Fredoka', sans-serif;">Verify your Aaj Ka Freelancer Account</h2>
            <p>Hi {username},</p>
            <p>Welcome to Aaj Ka Freelancer! Use the verification code below to complete your signup:</p>
            <p style="font-size: 2rem; font-weight: bold; background: #f0f0f0; padding: 10px; display: inline-block;">{code}</p>
            <p>This code will expire in 10 minutes.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <p style="margin-top: 30px;">— The Aaj Ka Freelancer Team</p>
            """
            msg.body = f"Hi {username},\n\nYour verification code is: {code}\n\nThis code will expire in 10 minutes."
            app = current_app._get_current_object()
            thread = threading.Thread(target=EmailService._send_email_async, args=(app, msg))
            thread.daemon = True
            thread.start()
            return True
        except Exception as e:
            logger.error(f"Failed to initiate async email: {e}")
            return False

    @staticmethod
    def send_welcome_email(email, username):
        msg = Message(
            subject="Welcome to Aaj Ka Freelancer!",
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[email],
        )
        msg.html = f"""
        <h2 style="color: #000; font-family: 'Fredoka', sans-serif;">Welcome to Aaj Ka Freelancer 🎉</h2>
        <p>Hi {username},</p>
        <p>Your account has been successfully verified.</p>
        <p>We're excited to have you onboard!</p>
        """
        msg.body = f"Hi {username},\n\nWelcome to Aaj Ka Freelancer! Your account is now verified."
        mail.send(msg)

    @staticmethod
    def send_welcome_email_async(email, username):
        try:
            msg = Message(
                subject="Welcome to Aaj Ka Freelancer!",
                sender=current_app.config['MAIL_DEFAULT_SENDER'],
                recipients=[email],
            )
            msg.html = f"""
            <h2 style="color: #000; font-family: 'Fredoka', sans-serif;">Welcome to Aaj Ka Freelancer 🎉</h2>
            <p>Hi {username},</p>
            <p>Your account has been successfully verified.</p>
            <p>We're excited to have you onboard!</p>
            """
            msg.body = f"Hi {username},\n\nWelcome to Aaj Ka Freelancer! Your account is now verified."
            app = current_app._get_current_object()
            thread = threading.Thread(target=EmailService._send_email_async, args=(app, msg))
            thread.daemon = True
            thread.start()
            return True
        except Exception as e:
            logger.error(f"Failed to initiate async welcome email: {e}")
            return False