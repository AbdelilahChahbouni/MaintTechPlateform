import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Production-grade configuration with seamless SQLite to PostgreSQL flexibility."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mainttech-morocco-industrial-secret-key-2026')
    
    # Database URL configuration (defaults to SQLite for dev, ready for PostgreSQL in Docker/Cloud)
    db_url = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'mainttech.db')}")
    # Fix Heroku/Render/AWS legacy postgres:// prefix if present
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Reconnect automatically if DB connection dropped
    } if not db_url.startswith("sqlite") else {}
    
    # Uploads configuration for technician CVs and profile photos
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'uploads', 'cvs'))
    AVATAR_UPLOAD_FOLDER = os.environ.get('AVATAR_UPLOAD_FOLDER', os.path.join(BASE_DIR, 'uploads', 'avatars'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

    # Session & Security Settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'

    # Cloud Proxy Support (e.g. AWS ALB, GCP Cloud Run, Traefik, Nginx)
    USE_PROXY_FIX = os.environ.get('USE_PROXY_FIX', 'True').lower() == 'true'
