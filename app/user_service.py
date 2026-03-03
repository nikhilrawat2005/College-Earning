import random
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
from flask import current_app
from app.extensions import db
from app.models import User, PendingUser, EmailVerification

class UserService:

    @staticmethod
    def generate_assigned_id(username, length_prefix=3, tries=30):
        prefix = (username.strip().lower() + 'x' * length_prefix)[:length_prefix]
        for _ in range(tries):
            num = f'{random.randint(0, 9999):04d}'
            candidate = prefix + num
            if not (User.query.filter_by(assigned_id=candidate).first() or
                    PendingUser.query.filter_by(assigned_id=candidate).first()):
                return candidate
        raise RuntimeError('Failed to generate unique assigned ID')

    @staticmethod
    def create_pending_user(username, email, password, full_name, college_name,
                            year, class_name, section, phone_number, short_bio, is_worker,
                            commit=True):
        assigned_id = UserService.generate_assigned_id(username)
        password_hash = generate_password_hash(password)

        pending = PendingUser(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            college_name=college_name,
            year=year,
            class_name=class_name,
            section=section,
            phone_number=phone_number,
            short_bio=short_bio,
            is_worker=is_worker,
            assigned_id=assigned_id
        )
        db.session.add(pending)
        if commit:
            db.session.commit()
        return pending

    @staticmethod
    def create_verification_code(pending_user_id, commit=True):
        code = f'{random.randint(0, 999999):06d}'
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        # Delete any existing codes for this pending user
        EmailVerification.query.filter_by(pending_user_id=pending_user_id).delete()

        verification = EmailVerification(
            pending_user_id=pending_user_id,
            code=code,
            expires_at=expires_at,
            last_sent_at=datetime.utcnow()
        )
        db.session.add(verification)
        if commit:
            db.session.commit()
        return code

    @staticmethod
    def verify_pending_user(pending_id, code):
        pending = PendingUser.query.get(pending_id)
        if not pending:
            return None, 'Invalid session'

        # Check if pending user itself has expired (older than 15 minutes)
        if datetime.utcnow() - pending.created_at > timedelta(minutes=15):
            db.session.delete(pending)
            db.session.commit()
            return None, 'Verification session expired. Please sign up again.'

        verification = EmailVerification.query.filter_by(
            pending_user_id=pending.id
        ).order_by(EmailVerification.created_at.desc()).first()

        if not verification or verification.is_expired():
            return None, 'Verification code expired'

        if verification.attempts >= 5:
            return None, 'Too many attempts'

        if verification.code != code:
            verification.attempts += 1
            db.session.commit()
            return None, 'Invalid verification code'

        if User.query.filter_by(email=pending.email).first() or User.query.filter_by(username=pending.username).first():
            db.session.delete(verification)
            pending.status = 'expired'
            db.session.commit()
            return None, 'User already exists'

        user = pending.to_user()
        db.session.add(user)
        db.session.delete(verification)
        db.session.delete(pending)
        db.session.commit()

        return user, 'Success'

    @staticmethod
    def authenticate_user(login_input, password):
        user = User.query.filter(
            (User.email == login_input) | (User.username == login_input)
        ).first()
        if user and check_password_hash(user.password_hash, password):
            return user
        return None

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username, is_verified=True).first()

    @staticmethod
    def search_users(query):
        if not query:
            return User.query.filter_by(is_verified=True).limit(20).all()
        return User.query.filter(
            (User.username.ilike(f'%{query}%')) |
            (User.full_name.ilike(f'%{query}%')) |
            (User.college_name.ilike(f'%{query}%'))
        ).filter_by(is_verified=True).all()

    @staticmethod
    def update_user_profile(user, data):
        user.full_name = data.get('full_name', user.full_name)
        user.college_name = data.get('college_name', user.college_name)
        user.year = data.get('year', user.year)
        user.class_name = data.get('class_name', user.class_name)
        user.section = data.get('section', user.section)
        user.phone_number = data.get('phone_number', user.phone_number)
        user.short_bio = data.get('short_bio', user.short_bio)
        user.is_worker = data.get('is_worker', user.is_worker)
        if 'skills' in data:
            user.skills = data.get('skills')
        db.session.commit()

    @staticmethod
    def change_password(user, new_password):
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

    @staticmethod
    def get_user_count():
        return User.query.filter_by(is_verified=True).count()

    @staticmethod
    def get_worker_count():
        return User.query.filter_by(is_verified=True, is_worker=True).count()

    # ==================== PROFILE IMAGE HELPERS ====================
    @staticmethod
    def save_profile_image(file, user_id):
        """
        Save an uploaded profile image: convert to JPEG, resize to max 500x500,
        compress with quality 85. Always saves as user_<id>.jpg.
        Returns the filename if successful, otherwise None.
        Raises ValueError for invalid file type.
        """
        if not file or file.filename == '':
            return None

        allowed_extensions = {'png', 'jpg', 'jpeg'}
        ext = file.filename.rsplit('.', 1)[1].lower()

        if ext not in allowed_extensions:
            raise ValueError("Invalid file type. Only PNG, JPG, JPEG allowed.")

        # Always save as .jpg
        filename = f"user_{user_id}.jpg"
        folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(folder, filename)

        # Open, convert to RGB, resize, and save as JPEG
        try:
            img = Image.open(file)
            img = img.convert('RGB')
            img.thumbnail((500, 500), Image.Resampling.LANCZOS)
            img.save(filepath, format='JPEG', quality=85, optimize=True)
        except Exception as e:
            current_app.logger.error(f"Image processing failed: {e}")
            raise IOError("Failed to process image.")

        if not os.path.exists(filepath):
            raise IOError("Failed to save image file.")

        return filename

    @staticmethod
    def delete_old_profile_image(user):
        """Delete old profile image if it exists and is not the default."""
        if user.profile_image and user.profile_image != 'default_profile.png':
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], user.profile_image)
            if os.path.exists(path):
                os.remove(path)

    @staticmethod
    def cleanup_expired_pending_users(minutes=15):
        """Delete pending users older than given minutes."""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        expired = PendingUser.query.filter(PendingUser.created_at < cutoff).all()
        for p in expired:
            db.session.delete(p)
        db.session.commit()
        return len(expired)