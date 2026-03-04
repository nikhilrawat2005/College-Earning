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
    year = db.Column(db.String(20), nullable=False)
    class_name = db.Column(db.String(20), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    short_bio = db.Column(db.Text)
    skills = db.Column(db.Text)
    is_worker = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_id = db.Column(db.String(50), unique=True)

    # Profile image fields
    profile_image = db.Column(db.String(255), nullable=False, default='default_profile.png')
    profile_crop_x = db.Column(db.Float, nullable=True)
    profile_crop_y = db.Column(db.Float, nullable=True)
    profile_crop_scale = db.Column(db.Float, nullable=True)

    # Relationships for hire requests
    sent_hire_requests = db.relationship('HireRequest', foreign_keys='HireRequest.sender_id', backref='sender', lazy='dynamic')
    received_hire_requests = db.relationship('HireRequest', foreign_keys='HireRequest.worker_id', backref='worker', lazy='dynamic')

    __table_args__ = (
        db.Index('idx_user_username', 'username'),
        db.Index('idx_user_email', 'email'),
        db.Index('idx_user_full_name', 'full_name'),
        db.Index('idx_user_college_name', 'college_name'),
    )


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

    __table_args__ = (
        db.Index('idx_emailverification_pending_user_id', 'pending_user_id'),
    )

    def is_expired(self):
        return datetime.utcnow() > self.expires_at


class HireRequest(db.Model):
    __tablename__ = 'hire_requests'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime, nullable=True)
    work_title = db.Column(db.String(200), nullable=True)
    work_description = db.Column(db.Text, nullable=True)
    active = db.Column(db.Boolean, default=True)

    # New fields for improved record workflow
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    record_created = db.Column(db.Boolean, default=False)

    # Relationships
    conversation = db.relationship('Conversation', backref='hire_requests')

    __table_args__ = (
        db.Index('idx_hire_sender', 'sender_id'),
        db.Index('idx_hire_worker', 'worker_id'),
        db.Index('idx_hire_conversation', 'conversation_id'),
        db.Index('idx_hire_status', 'status'),
    )

    @staticmethod
    def pending_count_for_worker(worker_id):
        """Return number of pending hire requests for a given worker."""
        return HireRequest.query.filter_by(
            worker_id=worker_id,
            status='pending',
            active=True
        ).count()