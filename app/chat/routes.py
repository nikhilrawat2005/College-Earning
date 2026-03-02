# app/chat/routes.py

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from app.chat import chat_bp
from app.chat.service import ChatService
from app.models import User
from app.extensions import db
from app.notifications.models import Notification
from app.chat.models import ConversationParticipant


# ===============================
# Chat List Page
# ===============================
@chat_bp.route('/')
@login_required
def index():
    conversations = ChatService.get_user_conversations(current_user.id)
    return render_template('chat_list.html', conversations=conversations)


# ===============================
# Open Conversation
# ===============================
@chat_bp.route('/<int:conversation_id>')
@login_required
def conversation(conversation_id):

    # ✅ Security check (user must belong to conversation)
    participant = ConversationParticipant.query.filter_by(
        conversation_id=conversation_id,
        user_id=current_user.id
    ).first()

    if not participant:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('chat.index'))

    conv_obj = participant.conversation

    # ✅ Load messages + mark messages read
    messages = ChatService.get_conversation_messages(
        conversation_id,
        current_user.id
    )

    # ✅ AUTO CLEAR MESSAGE NOTIFICATIONS
    Notification.query.filter(
        Notification.user_id == current_user.id,
        Notification.type == 'message',
        Notification.is_read == False
    ).update(
        {'is_read': True},
        synchronize_session=False
    )

    db.session.commit()

    # Find other user
    other_user = next(
        (p.user for p in conv_obj.participants
         if p.user_id != current_user.id),
        None
    )

    return render_template(
        'chat_room.html',
        conversation=conv_obj,
        messages=messages,
        other_user=other_user
    )


# ===============================
# Start Conversation
# ===============================
@chat_bp.route('/start/<int:user_id>')
@login_required
def start_conversation(user_id):

    if user_id == current_user.id:
        flash('You cannot message yourself.', 'info')
        return redirect(
            url_for('main.profile',
                    username=current_user.username)
        )

    User.query.get_or_404(user_id)

    conv = ChatService.get_or_create_conversation(
        current_user.id,
        user_id
    )

    return redirect(
        url_for('chat.conversation',
                conversation_id=conv.id)
    )


# ===============================
# Send Message (AJAX)
# ===============================
@chat_bp.route('/send/<int:conversation_id>', methods=['POST'])
@login_required
def send_message(conversation_id):

    message = request.form.get('message', '').strip()

    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    msg = ChatService.send_message(
        conversation_id,
        current_user.id,
        message
    )

    return jsonify({
        'id': msg.id,
        'message_text': msg.message_text,
        'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'sender_id': msg.sender_id
    })


# ===============================
# Poll New Messages (Realtime)
# ===============================
@chat_bp.route('/<int:conversation_id>/messages')
@login_required
def get_new_messages(conversation_id):

    since_id = request.args.get('since', 0, type=int)

    messages = ChatService.get_messages_since(
        conversation_id,
        since_id,
        current_user.id
    )

    data = [{
        'id': m.id,
        'message_text': m.message_text,
        'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'sender_id': m.sender_id
    } for m in messages]

    return jsonify(data)


# ===============================
# Unread Message Count
# ===============================
@chat_bp.route('/unread-count')
@login_required
def unread_count():
    count = ChatService.get_unread_count(current_user.id)
    return jsonify({'count': count})