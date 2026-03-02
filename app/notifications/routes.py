# app/notifications/routes.py

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.notifications.service import NotificationService

notifications_bp = Blueprint(
    'notifications',
    __name__,
    url_prefix='/notifications'
)


@notifications_bp.route('/unread')
@login_required
def unread():
    notifs = NotificationService.get_unread_notifications(current_user.id)

    data = [{
        'id': n.id,
        'type': n.type,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'reference_id': n.reference_id
    } for n in notifs]

    return jsonify({
        'count': len(notifs),
        'notifications': data
    })


@notifications_bp.route('/mark-read', methods=['POST'])
@login_required
def mark_read():
    data = request.get_json() or {}

    if data.get('all'):
        NotificationService.mark_all_as_read(current_user.id)

    elif 'id' in data:
        NotificationService.mark_as_read(data['id'])

    return jsonify({'success': True})