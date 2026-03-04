# app/chat/routes.py

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from app.chat import chat_bp
from app.chat.service import ChatService
from app.models import User, HireRequest
from app.extensions import db
from app.notifications.models import Notification
from app.chat.models import ConversationParticipant


# ===============================
# Existing routes (unchanged)
# ===============================

@chat_bp.route('/')
@login_required
def index():
    conversations = ChatService.get_user_conversations(current_user.id)
    return render_template('chat_list.html', conversations=conversations)


@chat_bp.route('/<int:conversation_id>')
@login_required
def conversation(conversation_id):
    participant = ConversationParticipant.query.filter_by(
        conversation_id=conversation_id,
        user_id=current_user.id
    ).first()
    if not participant:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('chat.index'))

    conv_obj = participant.conversation
    messages = ChatService.get_conversation_messages(conversation_id, current_user.id)

    # Clear message notifications
    Notification.query.filter(
        Notification.user_id == current_user.id,
        Notification.type == 'message',
        Notification.is_read == False
    ).update({'is_read': True}, synchronize_session=False)
    db.session.commit()

    other_user = next(
        (p.user for p in conv_obj.participants if p.user_id != current_user.id),
        None
    )

    return render_template(
        'chat_room.html',
        conversation=conv_obj,
        messages=messages,
        other_user=other_user
    )


@chat_bp.route('/start/<int:user_id>')
@login_required
def start_conversation(user_id):
    if user_id == current_user.id:
        flash('You cannot message yourself.', 'info')
        return redirect(url_for('main.profile', username=current_user.username))

    User.query.get_or_404(user_id)
    conv = ChatService.get_or_create_conversation(current_user.id, user_id)
    return redirect(url_for('chat.conversation', conversation_id=conv.id))


@chat_bp.route('/send/<int:conversation_id>', methods=['POST'])
@login_required
def send_message(conversation_id):
    message = request.form.get('message', '').strip()
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    msg = ChatService.send_message(conversation_id, current_user.id, message)
    return jsonify({
        'id': msg.id,
        'message_text': msg.message_text,
        'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'sender_id': msg.sender_id
    })


@chat_bp.route('/<int:conversation_id>/messages')
@login_required
def get_new_messages(conversation_id):
    since_id = request.args.get('since', 0, type=int)
    messages = ChatService.get_messages_since(conversation_id, since_id, current_user.id)
    data = [{
        'id': m.id,
        'message_text': m.message_text,
        'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'sender_id': m.sender_id
    } for m in messages]
    return jsonify(data)


@chat_bp.route('/unread-count')
@login_required
def unread_count():
    count = ChatService.get_unread_count(current_user.id)
    return jsonify({'count': count})


# ===============================
# HIRE REQUEST ENDPOINTS (updated)
# ===============================

@chat_bp.route('/hire/request/<int:conversation_id>', methods=['POST'])
@login_required
def hire_request(conversation_id):
    """Send a hire request to the worker in this conversation."""
    participant = ConversationParticipant.query.filter_by(
        conversation_id=conversation_id,
        user_id=current_user.id
    ).first()
    if not participant:
        return jsonify({'error': 'Unauthorized'}), 403

    conv = participant.conversation
    other_user = None
    for p in conv.participants:
        if p.user_id != current_user.id:
            other_user = p.user
            break
    if not other_user:
        return jsonify({'error': 'Conversation has no other participant'}), 400

    if not other_user.is_worker:
        return jsonify({'error': 'This user is not a worker'}), 400

    if other_user.id == current_user.id:
        return jsonify({'error': 'You cannot hire yourself'}), 400

    # Check for existing pending request in this conversation
    existing = HireRequest.query.filter_by(
        conversation_id=conversation_id,
        status='pending',
        active=True
    ).first()
    if existing:
        return jsonify({'error': 'A pending hire request already exists'}), 400

    hire = HireRequest(
        sender_id=current_user.id,
        worker_id=other_user.id,
        conversation_id=conversation_id,
        status='pending',
        active=True
    )
    db.session.add(hire)
    db.session.commit()

    return jsonify({
        'success': True,
        'request_id': hire.id,
        'status': hire.status
    })


@chat_bp.route('/hire/status/<int:conversation_id>')
@login_required
def hire_status(conversation_id):
    """Get the current hire request status for this conversation."""
    participant = ConversationParticipant.query.filter_by(
        conversation_id=conversation_id,
        user_id=current_user.id
    ).first()
    if not participant:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get the most recent active request (pending or accepted)
    hire = HireRequest.query.filter_by(
        conversation_id=conversation_id,
        active=True
    ).order_by(HireRequest.created_at.desc()).first()

    # If no active request, check for any accepted request with record (inactive) for view
    if not hire:
        hire = HireRequest.query.filter_by(
            conversation_id=conversation_id,
            record_created=True
        ).order_by(HireRequest.created_at.desc()).first()

    if not hire:
        return jsonify({'status': None})

    # Determine if current user is the requester
    is_requester = (hire.sender_id == current_user.id)

    return jsonify({
        'status': hire.status if hire.active else None,  # if inactive, treat as no active request for hire button
        'request_id': hire.id,
        'work_title': hire.work_title,
        'work_description': hire.work_description,
        'start_date': hire.start_date.isoformat() if hire.start_date else None,
        'end_date': hire.end_date.isoformat() if hire.end_date else None,
        'record_created': hire.record_created,
        'is_requester': is_requester,
        'active': hire.active
    })


@chat_bp.route('/hire/accept/<int:request_id>', methods=['POST'])
@login_required
def accept_hire(request_id):
    hire = HireRequest.query.get_or_404(request_id)
    if hire.worker_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if hire.status != 'pending':
        return jsonify({'error': 'Request is not pending'}), 400

    hire.status = 'accepted'
    hire.responded_at = datetime.utcnow()
    hire.active = True
    db.session.commit()

    return jsonify({'success': True, 'status': hire.status})


@chat_bp.route('/hire/reject/<int:request_id>', methods=['POST'])
@login_required
def reject_hire(request_id):
    hire = HireRequest.query.get_or_404(request_id)
    if hire.worker_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if hire.status != 'pending':
        return jsonify({'error': 'Request is not pending'}), 400

    hire.status = 'rejected'
    hire.responded_at = datetime.utcnow()
    hire.active = False
    db.session.commit()

    return jsonify({'success': True})


@chat_bp.route('/hire/record/<int:request_id>', methods=['POST'])
@login_required
def record_hire(request_id):
    """Save work record (title, dates) after acceptance. Only requester can do this."""
    hire = HireRequest.query.get_or_404(request_id)
    # Only the requester can create the record
    if hire.sender_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if hire.status != 'accepted':
        return jsonify({'error': 'Request is not accepted'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    hire.work_title = data.get('title', '').strip()
    hire.work_description = data.get('description', '').strip()  # optional notes
    hire.start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date() if data.get('start_date') else None
    hire.end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date() if data.get('end_date') else None
    hire.record_created = True
    hire.active = False  # Mark as inactive so new requests can be made
    db.session.commit()

    return jsonify({'success': True})