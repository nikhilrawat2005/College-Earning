# app/notifications/service.py
from app.extensions import db
from app.notifications.models import Notification
from datetime import datetime

class NotificationService:

    @staticmethod
    def create_notification(user_id, type, reference_id=None):
        notif = Notification(
            user_id=user_id,
            type=type,
            reference_id=reference_id,
            is_read=False
        )
        db.session.add(notif)
        db.session.commit()
        return notif

    @staticmethod
    def get_unread_notifications(user_id):
        return Notification.query.filter_by(user_id=user_id, is_read=False).order_by(Notification.created_at.desc()).all()

    @staticmethod
    def mark_all_as_read(user_id):
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()

    @staticmethod
    def mark_as_read(notification_id):
        notif = Notification.query.get(notification_id)
        if notif:
            notif.is_read = True
            db.session.commit()