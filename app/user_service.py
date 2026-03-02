import random
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
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

    # Profile image helpers
    @staticmethod
    def save_profile_image(file, user_id, crop_data=None):
        """Save uploaded image, apply crop if provided, return filename."""
        if not file:
            return None
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"user_{user_id}_{secure_filename(file.filename)}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if crop_data:
            # Crop using Pillow
            im = Image.open(filepath)
            x, y, scale = crop_data['x'], crop_data['y'], crop_data['scale']
            # Simple crop: assume square crop from center
            width, height = im.size
            left = max(0, x)
            top = max(0, y)
            right = min(width, left + scale)
            bottom = min(height, top + scale)
            im = im.crop((left, top, right, bottom))
            im.save(filepath)

        return filename

    @staticmethod
    def delete_old_profile_image(user):
        if user.profile_image:
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], user.profile_image)
            if os.path.exists(path):
                os.remove(path)