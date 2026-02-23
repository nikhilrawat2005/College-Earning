from flask import Flask, render_template
from config import Config
from app.extensions import db, mail, login_manager, limiter

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    limiter.init_app(app)

    # Import models to ensure they are registered with SQLAlchemy
    from app import models

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(models.User, int(user_id))

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error='Page not found'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', error='Internal server error'), 500

    # Create tables (only if they don't exist)
    with app.app_context():
        db.create_all()

    return app