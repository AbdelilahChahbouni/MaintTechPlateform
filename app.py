import os
from flask import Flask, render_template
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from models import db, User
from routes import main_bp

def create_app(config_class=Config):
    """Application factory for MaintTech Jobs Maroc."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable ProxyFix when running behind reverse proxies in Cloud/Docker (Cloud Run, AWS, Traefik, Nginx)
    if app.config.get('USE_PROXY_FIX', True):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

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

    # Custom Error Handlers
    @app.errorhandler(404)
    def handle_404(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def handle_500(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(413)
    def handle_413(e):
        return render_template('errors/413.html'), 413

    # Create tables automatically on startup if not present
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    print("==================================================")
    print("  MAINTTECH JOBS - MAROC INDUSTRIAL MARKETPLACE  ")
    print(f"  Server running on http://{host}:{port}        ")
    print("==================================================")
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true', host=host, port=port)
