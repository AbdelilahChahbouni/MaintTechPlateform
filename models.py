import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """
    User model representing both industrial technicians and recruiters.
    Supports secure password hashing and role-based access control.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'technician' or 'recruiter'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 1-to-1 relationships with role profiles
    technician_profile = db.relationship(
        'TechnicianProfile',
        backref='user',
        uselist=False,
        cascade='all, delete-orphan'
    )
    recruiter_profile = db.relationship(
        'RecruiterProfile',
        backref='user',
        uselist=False,
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        """Hashes the user password using Werkzeug."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies the password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_technician(self):
        return self.role == 'technician'

    @property
    def is_recruiter(self):
        return self.role == 'recruiter'

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class TechnicianProfile(db.Model):
    """
    Technician profile storing Moroccan industrial technician qualifications,
    specialties, verified skills, and experience.
    """
    __tablename__ = 'technician_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    city = db.Column(db.String(80), nullable=True)  # Casablanca, Tanger, Kénitra, Meknès, etc.
    specialty = db.Column(db.String(100), nullable=True)  # Electromécanique, Automatisme, CNC, etc.
    skills = db.Column(db.Text, nullable=True)  # Stored as JSON array or comma-separated values
    experience_years = db.Column(db.Integer, default=0)
    mobility = db.Column(db.Boolean, default=True)  # Mobile across Morocco or industrial zones
    cv_filename = db.Column(db.String(255), nullable=True)
    photo_filename = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)

    @property
    def skills_list(self):
        """Returns the list of skills from JSON array string or CSV string."""
        if not self.skills:
            return []
        try:
            data = json.loads(self.skills)
            if isinstance(data, list):
                return [s.strip() for s in data if s.strip()]
        except (json.JSONDecodeError, TypeError):
            pass
        # Fallback to comma-separated list
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def set_skills(self, skills_input):
        """Serializes a list or comma-separated string into a JSON list."""
        if isinstance(skills_input, list):
            clean_list = [s.strip() for s in skills_input if s.strip()]
        elif isinstance(skills_input, str):
            clean_list = [s.strip() for s in skills_input.split(',') if s.strip()]
        else:
            clean_list = []
        self.skills = json.dumps(clean_list, ensure_ascii=False)

    @property
    def anonymous_name(self):
        """Formats the technician's name for privacy on public listings (e.g. Karim A.)."""
        parts = self.full_name.strip().split()
        if len(parts) >= 2:
            return f"{parts[0]} {parts[1][0].upper()}."
        return self.full_name

    def to_dict(self, include_contact=False):
        """Serializes profile into dictionary for the Dynamic Fetch API."""
        return {
            'id': self.id,
            'full_name': self.full_name if include_contact else self.anonymous_name,
            'anonymous_name': self.anonymous_name,
            'city': self.city or 'Maroc',
            'specialty': self.specialty or 'Maintenance Industrielle',
            'skills': self.skills_list,
            'experience_years': self.experience_years or 0,
            'mobility': bool(self.mobility),
            'cv_available': bool(self.cv_filename),
            'cv_filename': self.cv_filename,
            'photo_filename': self.photo_filename,
            'has_photo': bool(self.photo_filename),
            'bio': self.bio or '',
            'phone': self.phone if include_contact else None,
            'email': self.user.email if include_contact and self.user else None,
            'created_at': self.user.created_at.strftime('%Y-%m-%d') if self.user and self.user.created_at else None
        }

    def __repr__(self):
        return f"<TechnicianProfile {self.full_name} - {self.specialty} ({self.city})>"


class RecruiterProfile(db.Model):
    """
    Recruiter profile for Moroccan industrial plants, factories, and HR recruiters.
    """
    __tablename__ = 'recruiter_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    company_name = db.Column(db.String(150), nullable=False)
    industry_type = db.Column(db.String(100), nullable=True)  # Automobile, Aéronautique, etc.
    city = db.Column(db.String(80), nullable=True)
    phone = db.Column(db.String(30), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'industry_type': self.industry_type,
            'city': self.city,
            'phone': self.phone
        }

    def __repr__(self):
        return f"<RecruiterProfile {self.company_name} ({self.city})>"
