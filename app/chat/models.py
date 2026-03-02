from datetime import datetime
from app.extensions import db

class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    participants = db.relationship('ConversationParticipant', back_populates='conversation', cascade='all, delete-orphan')
    messages = db.relationship('Message', back_populates='conversation', cascade='all, delete-orphan', order_by='Message.timestamp')

class ConversationParticipant(db.Model):
    __tablename__ = 'conversation_participants'
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    conversation = db.relationship('Conversation', back_populates='participants')
    user = db.relationship('User', backref='chat_participations')

    __table_args__ = (
        db.Index('idx_conversationparticipant_user_id', 'user_id'),
    )

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    conversation = db.relationship('Conversation', back_populates='messages')
    sender = db.relationship('User', foreign_keys=[sender_id])

    __table_args__ = (
        db.Index('idx_message_conversation_id', 'conversation_id'),
        db.Index('idx_message_sender_id', 'sender_id'),
    )