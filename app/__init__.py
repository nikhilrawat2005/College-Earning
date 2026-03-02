from flask import Flask, render_template
from config import Config
from app.extensions import db, mail, login_manager, limiter, migrate, csrf
from app.services.skill_service import SkillService
import os


def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static'
    )

    app.config.from_object(config_class)

    # ===============================
    # Initialize Extensions
    # ===============================
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    # Pass storage_uri from config to limiter
    limiter.storage_uri = app.config['RATELIMIT_STORAGE_URI']
    limiter.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'

    # ===============================
    # Create upload folders if missing
    # ===============================
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['TEMP_UPLOAD_FOLDER'], exist_ok=True)

    # ===============================
    # Import Models (REGISTER TABLES)
    # ===============================
    from app import models
    from app.chat import models as chat_models
    from app.notifications import models as notif_models

    # ===============================
    # SAFE USER LOADER (DB RESET SAFE)
    # ===============================
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(models.User, int(user_id))
        except Exception:
            return None

    # ===============================
    # Register Blueprints
    # ===============================
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.chat import chat_bp
    from app.notifications import notifications_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(notifications_bp)

    # ===============================
    # Context Processor for Unread Messages
    # ===============================
    @app.context_processor
    def inject_unread_count():
        from flask_login import current_user  # <-- IMPORT ADDED HERE
        if current_user.is_authenticated:
            from app.chat.service import ChatService
            count = ChatService.get_unread_count(current_user.id)
            return {'unread_messages_count': count}
        return {'unread_messages_count': 0}

    # ===============================
    # Jinja Filter
    # ===============================
    def skill_description_filter(skill):
        return SkillService.get_description(skill)

    app.jinja_env.filters['skill_description'] = skill_description_filter

    # ===============================
    # Error Handlers
    # ===============================
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error='Page not found'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', error='Internal server error'), 500

    # ===============================
    # ✅ AUTO CREATE DATABASE TABLES (development only)
    # ===============================
    with app.app_context():
        db.create_all()

    return app