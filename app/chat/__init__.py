# app/chat/__init__.py
from flask import Blueprint

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

from app.chat import routes