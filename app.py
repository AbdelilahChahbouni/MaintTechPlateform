import os
from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User
from routes import main_bp

def create_app(config_class=Config):
    """Application factory for MaintTech Jobs Maroc."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
    login_manager.login_message_category = "info"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Ensure upload directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    if 'AVATAR_UPLOAD_FOLDER' in app.config:
        os.makedirs(app.config['AVATAR_UPLOAD_FOLDER'], exist_ok=True)

    # Register Blueprints
    app.register_blueprint(main_bp)

    # Create tables automatically on startup if not present
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    print("==================================================")
    print("  MAINTTECH JOBS - MAROC INDUSTRIAL MARKETPLACE  ")
    print("  Server running on http://127.0.0.1:5000       ")
    print("==================================================")
    app.run(debug=True, host='127.0.0.1', port=5000)
