from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
# Initialize limiter without storage_uri – will be set from config in create_app
limiter = Limiter(key_func=get_remote_address)
migrate = Migrate()
csrf = CSRFProtect()