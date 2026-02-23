from datetime import datetime
from flask_login import UserMixin
from app.extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    college_name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(20), nullable=False)          # e.g., "1st Year"
    class_name = db.Column(db.String(20), nullable=False)    # e.g., "Computer Science"
    section = db.Column(db.String(10), nullable=False)       # e.g., "A"
    phone_number = db.Column(db.String(20), nullable=False)
    short_bio = db.Column(db.Text)
    skills = db.Column(db.Text)                               # comma‑separated list
    is_worker = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_id = db.Column(db.String(50), unique=True)


class PendingUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    college_name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(20), nullable=False)
    class_name = db.Column(db.String(20), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    short_bio = db.Column(db.Text)
    is_worker = db.Column(db.Boolean, default=False)
    assigned_id = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')

    def to_user(self):
        return User(
            username=self.username,
            email=self.email,
            password_hash=self.password_hash,
            full_name=self.full_name,
            college_name=self.college_name,
            year=self.year,
            class_name=self.class_name,
            section=self.section,
            phone_number=self.phone_number,
            short_bio=self.short_bio,
            is_worker=self.is_worker,
            assigned_id=self.assigned_id,
            is_verified=True
        )


class EmailVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pending_user_id = db.Column(db.Integer, db.ForeignKey('pending_user.id'), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0)
    last_sent_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_expired(self):
        return datetime.utcnow() > self.expires_at