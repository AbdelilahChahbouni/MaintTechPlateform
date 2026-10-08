import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Application configuration with seamless SQLite to PostgreSQL flexibility."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mainttech-morocco-industrial-secret-key-2026')
    
    # Database URL configuration (defaults to SQLite, ready for PostgreSQL)
    db_url = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'mainttech.db')}")
    # Fix Heroku/Render legacy postgres:// prefix if present
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads configuration for technician CVs and profile photos
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'cvs')
    AVATAR_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'avatars')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
