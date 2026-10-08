import os
import time
from flask import (
    Blueprint, render_template, request, redirect, url_for, 
    flash, jsonify, current_app, send_from_directory, abort
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, TechnicianProfile, RecruiterProfile

main_bp = Blueprint('main', __name__)

def allowed_file(filename):
    """Check if uploaded file has an allowed extension."""
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'doc', 'docx'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

def allowed_image(filename):
    """Check if uploaded image file has an allowed extension."""
    allowed = current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', {'png', 'jpg', 'jpeg', 'webp', 'gif'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


# ==========================================
# PUBLIC ROUTES
# ==========================================

@main_bp.route('/')
def index():
    """
    Public Landing Page:
    Displays Moroccan industrial value proposition, industry metrics, 
    and dynamically features the top 3 experienced technicians.
    """
    top_talents = TechnicianProfile.query.order_by(
        TechnicianProfile.experience_years.desc()
    ).limit(3).all()
    
    total_technicians = TechnicianProfile.query.count()
    total_recruiters = RecruiterProfile.query.count()

    return render_template(
        'index.html',
        top_talents=top_talents,
        total_technicians=total_technicians,
        total_recruiters=total_recruiters
    )


# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User Registration:
    Supports dual role selection ('technician' vs 'recruiter')
    Creates the User and respective Profile in a single database transaction.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        role = request.form.get('role', 'technician').strip().lower()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Basic validations
        if not email or not password:
            flash("Veuillez remplir tous les champs obligatoires.", "danger")
            return render_template('register.html', role=role)

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return render_template('register.html', role=role, email=email)

        if len(password) < 6:
            flash("Le mot de passe doit contenir au moins 6 caractères.", "danger")
            return render_template('register.html', role=role, email=email)

        if User.query.filter_by(email=email).first():
            flash("Cette adresse email est déjà enregistrée. Veuillez vous connecter.", "warning")
            return redirect(url_for('main.login'))

        # Create user
        user = User(email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Get user.id for profile creation

        if role == 'technician':
            full_name = request.form.get('full_name', '').strip() or email.split('@')[0].capitalize()
            city = request.form.get('city', 'Casablanca')
            specialty = request.form.get('specialty', 'Electromécanique')
            tech_profile = TechnicianProfile(
                user_id=user.id,
                full_name=full_name,
                city=city,
                specialty=specialty,
                mobility=True,
                experience_years=int(request.form.get('experience_years') or 1)
            )
            # Default starter skills based on specialty
            tech_profile.set_skills(["Diagnostic & Dépannage", "Lecture de Schémas"])
            db.session.add(tech_profile)
        else:
            company_name = request.form.get('company_name', '').strip() or "Entreprise Industrielle"
            industry_type = request.form.get('industry_type', 'Automobile')
            city = request.form.get('city', 'Tanger')
            recruiter_profile = RecruiterProfile(
                user_id=user.id,
                company_name=company_name,
                industry_type=industry_type,
                city=city,
                phone=request.form.get('phone', '')
            )
            db.session.add(recruiter_profile)

        db.session.commit()
        login_user(user)
        flash("Compte créé avec succès ! Bienvenue sur MaintTech Jobs Maroc.", "success")
        return redirect(url_for('main.dashboard'))

    # Pre-select role if specified in query params (e.g. /register?role=recruiter)
    role_param = request.args.get('role', 'technician')
    return render_template('register.html', role=role_param)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User Login: Authenticates technicians and recruiters."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f"Ravi de vous revoir ! Connecté en tant que {user.role.capitalize()}.", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash("Identifiants invalides. Veuillez vérifier votre email et mot de passe.", "danger")

    return render_template('login.html')


@main_bp.route('/logout')
@login_required
def logout():
    """User Logout."""
    logout_user()
    flash("Vous avez été déconnecté avec succès.", "info")
    return redirect(url_for('main.index'))


# ==========================================
# DASHBOARD FLOWS (TECHNICIAN & RECRUITER)
# ==========================================

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Unified Dashboard dispatcher based on role."""
    if current_user.is_technician:
        return redirect(url_for('main.technician_dashboard'))
    elif current_user.is_recruiter:
        return redirect(url_for('main.recruiter_dashboard'))
    return render_template('dashboard.html')


@main_bp.route('/dashboard/technician', methods=['GET', 'POST'])
@login_required
def technician_dashboard():
    """
    Technician Dashboard:
    Profile management, skills tagging (PLCs, VFDs, Pneumatics, CNC),
    experience, mobility, and CV upload.
    """
    if not current_user.is_technician:
        flash("Cette section est réservée aux techniciens de maintenance.", "warning")
        return redirect(url_for('main.recruiter_dashboard'))

    profile = current_user.technician_profile
    if not profile:
        profile = TechnicianProfile(
            user_id=current_user.id,
            full_name=current_user.email.split('@')[0].capitalize()
        )
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        profile.full_name = request.form.get('full_name', profile.full_name).strip()
        profile.phone = request.form.get('phone', '').strip()
        profile.city = request.form.get('city', '').strip()
        profile.specialty = request.form.get('specialty', '').strip()
        profile.experience_years = int(request.form.get('experience_years') or 0)
        profile.mobility = bool(request.form.get('mobility'))
        profile.bio = request.form.get('bio', '').strip()

        # Handle skills: combines selected predefined tags with custom tags
        selected_skills = request.form.getlist('skills_tags')
        custom_skills = request.form.get('custom_skills', '')
        if custom_skills:
            for item in custom_skills.split(','):
                cleaned = item.strip()
                if cleaned and cleaned not in selected_skills:
                    selected_skills.append(cleaned)
        profile.set_skills(selected_skills)

        # Handle CV File Upload
        if 'cv_file' in request.files:
            file = request.files['cv_file']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Unique filename prefix to avoid collisions
                    unique_filename = f"cv_{current_user.id}_{int(time.time())}_{filename}"
                    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                    
                    # Ensure directory exists
                    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                    file.save(upload_path)
                    
                    # Remove old file if exists
                    if profile.cv_filename:
                        old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], profile.cv_filename)
                        if os.path.exists(old_file_path):
                            try:
                                os.remove(old_file_path)
                            except OSError:
                                pass

                    profile.cv_filename = unique_filename
                    flash("Votre CV a été téléversé avec succès !", "info")
                else:
                    flash("Format de fichier non supporté. Veuillez envoyer un PDF, DOC ou DOCX.", "danger")

        # Handle Profile Photo Upload
        if 'photo_file' in request.files:
            photo = request.files['photo_file']
            if photo and photo.filename != '':
                if allowed_image(photo.filename):
                    p_filename = secure_filename(photo.filename)
                    unique_photo_name = f"avatar_{current_user.id}_{int(time.time())}_{p_filename}"
                    avatar_dir = current_app.config['AVATAR_UPLOAD_FOLDER']
                    os.makedirs(avatar_dir, exist_ok=True)
                    photo_path = os.path.join(avatar_dir, unique_photo_name)
                    photo.save(photo_path)

                    # Remove old photo if exists
                    if profile.photo_filename:
                        old_photo_path = os.path.join(avatar_dir, profile.photo_filename)
                        if os.path.exists(old_photo_path):
                            try:
                                os.remove(old_photo_path)
                            except OSError:
                                pass

                    profile.photo_filename = unique_photo_name
                    flash("Photo de profil mise à jour avec succès !", "info")
                else:
                    flash("Format d'image non supporté. Veuillez choisir une image PNG, JPG, JPEG ou WEBP.", "danger")

        db.session.commit()
        flash("Votre profil de technicien a été mis à jour avec succès !", "success")
        return redirect(url_for('main.technician_dashboard'))

    # Predefined common Moroccan industrial skills for interactive tags
    popular_skills = [
        "Siemens TIA Portal (S7-1200/1500)", "Schneider Electric SoMachine", "Festo Pneumatique",
        "Variateurs Schneider Altivar", "Hydraulique Bosch Rexroth", "Lectra Vector (Découpe)",
        "Robotique KUKA", "Robotique Fanuc", "CNC Heidenhain / Fanuc", "GMAO Coswin",
        "GMAO SAP PM", "Omron Sysmac Studio", "Réseaux Profinet / Modbus", "Alignement Laser"
    ]

    return render_template(
        'dashboard.html',
        profile=profile,
        popular_skills=popular_skills,
        is_technician=True
    )


@main_bp.route('/dashboard/recruiter', methods=['GET', 'POST'])
@login_required
def recruiter_dashboard():
    """
    Recruiter Dashboard:
    Company profile management and direct access to talent search.
    """
    if not current_user.is_recruiter:
        flash("Cette section est réservée aux recruteurs industriels.", "warning")
        return redirect(url_for('main.technician_dashboard'))

    profile = current_user.recruiter_profile
    if not profile:
        profile = RecruiterProfile(
            user_id=current_user.id,
            company_name="Mon Entreprise Industrielle"
        )
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        profile.company_name = request.form.get('company_name', profile.company_name).strip()
        profile.industry_type = request.form.get('industry_type', '').strip()
        profile.city = request.form.get('city', '').strip()
        profile.phone = request.form.get('phone', '').strip()

        db.session.commit()
        flash("Profil recruteur mis à jour avec succès !", "success")
        return redirect(url_for('main.recruiter_dashboard'))

    recent_talents = TechnicianProfile.query.order_by(TechnicianProfile.id.desc()).limit(4).all()
    total_talents = TechnicianProfile.query.count()

    return render_template(
        'dashboard.html',
        profile=profile,
        recent_talents=recent_talents,
        total_talents=total_talents,
        is_recruiter=True
    )


# ==========================================
# RECRUITER FLOW & DYNAMIC SEARCH ENGINE
# ==========================================

@main_bp.route('/talents')
def talents():
    """
    Talent Marketplace Page:
    Showcases technician cards with dynamic client-side filtering via Vanilla JS Fetch API.
    Provides initial pre-rendered cards and metadata for instant SEO and zero-JS fallback.
    """
    # Metadata for filter selects
    cities = [c[0] for c in db.session.query(TechnicianProfile.city).distinct() if c[0]]
    specialties = [s[0] for s in db.session.query(TechnicianProfile.specialty).distinct() if s[0]]
    
    # Common standard options if DB has few
    default_cities = ["Casablanca", "Tanger", "Kénitra", "Meknès", "Fès", "Rabat", "Jorf Lasfar"]
    for dc in default_cities:
        if dc not in cities:
            cities.append(dc)
            
    default_specialties = [
        "Electromécanique", "Automatisme", "Maintenance Mécanique", 
        "Hydraulique/Pneumatique", "CNC / Commande Numérique", "Découpe Automatique (Lectra)"
    ]
    for ds in default_specialties:
        if ds not in specialties:
            specialties.append(ds)

    cities.sort()
    specialties.sort()

    initial_talents = TechnicianProfile.query.order_by(
        TechnicianProfile.experience_years.desc()
    ).all()

    return render_template(
        'talents.html',
        cities=cities,
        specialties=specialties,
        initial_talents=initial_talents
    )


@main_bp.route('/api/talents')
def api_talents():
    """
    Dynamic API Endpoint GET /api/talents:
    Accepts query parameters:
      - city: filter by city (case-insensitive)
      - specialty: filter by specialty (case-insensitive)
      - min_exp: minimum years of experience
      - search: free-text search in full_name, skills, bio, specialty
      - mobility: boolean ('true' / 'false')
    Returns JSON response for instant client-side filtering.
    """
    city = request.args.get('city', '').strip()
    specialty = request.args.get('specialty', '').strip()
    min_exp = request.args.get('min_exp', '').strip()
    search = request.args.get('search', '').strip()
    mobility = request.args.get('mobility', '').strip()

    query = TechnicianProfile.query

    if city and city != 'all':
        query = query.filter(TechnicianProfile.city.ilike(f"%{city}%"))

    if specialty and specialty != 'all':
        query = query.filter(TechnicianProfile.specialty.ilike(f"%{specialty}%"))

    if min_exp:
        try:
            min_exp_val = int(min_exp)
            if min_exp_val > 0:
                query = query.filter(TechnicianProfile.experience_years >= min_exp_val)
        except ValueError:
            pass

    if mobility.lower() in ['true', '1']:
        query = query.filter(TechnicianProfile.mobility == True)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                TechnicianProfile.full_name.ilike(search_pattern),
                TechnicianProfile.specialty.ilike(search_pattern),
                TechnicianProfile.city.ilike(search_pattern),
                TechnicianProfile.skills.ilike(search_pattern),
                TechnicianProfile.bio.ilike(search_pattern)
            )
        )

    talents_list = query.order_by(TechnicianProfile.experience_years.desc()).all()

    # If logged in as recruiter, include complete contact details; otherwise anonymous
    include_contact = current_user.is_authenticated and current_user.is_recruiter

    data = [t.to_dict(include_contact=include_contact) for t in talents_list]

    return jsonify({
        'success': True,
        'count': len(data),
        'is_recruiter': include_contact,
        'talents': data
    })


@main_bp.route('/talents/<int:talent_id>')
def talent_detail(talent_id):
    """
    Detailed profile view of an industrial maintenance technician.
    Shows contact info & CV download if current user is an authenticated recruiter.
    """
    talent = TechnicianProfile.query.get_or_404(talent_id)
    is_recruiter = current_user.is_authenticated and current_user.is_recruiter
    is_owner = current_user.is_authenticated and current_user.id == talent.user_id

    return render_template(
        'talent_detail.html',
        talent=talent,
        can_view_contact=(is_recruiter or is_owner)
    )


@main_bp.route('/download/cv/<int:talent_id>')
def download_cv(talent_id):
    """Secure CV download for registered recruiters or the profile owner."""
    talent = TechnicianProfile.query.get_or_404(talent_id)

    if not talent.cv_filename:
        flash("Aucun CV n'a été déposé pour ce profil.", "warning")
        return redirect(url_for('main.talent_detail', talent_id=talent_id))

    # Security check: must be logged in as recruiter or profile owner
    if not current_user.is_authenticated:
        flash("Veuillez vous connecter en tant que recruteur pour télécharger les CVs.", "warning")
        return redirect(url_for('main.login', next=request.url))

    if not (current_user.is_recruiter or current_user.id == talent.user_id):
        flash("Accès réservé aux recruteurs d'entreprises.", "danger")
        return redirect(url_for('main.talent_detail', talent_id=talent_id))

    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, talent.cv_filename)

    if not os.path.exists(file_path):
        flash("Le fichier CV est introuvable sur le serveur.", "danger")
        return redirect(url_for('main.talent_detail', talent_id=talent_id))

    download_name = f"CV_{secure_filename(talent.full_name)}_{talent.specialty}.{talent.cv_filename.rsplit('.', 1)[1]}"
    return send_from_directory(
        upload_folder,
        talent.cv_filename,
        as_attachment=True,
        download_name=download_name
    )


@main_bp.route('/uploads/avatars/<filename>')
def serve_avatar(filename):
    """Serve uploaded technician avatar pictures."""
    avatar_dir = current_app.config.get('AVATAR_UPLOAD_FOLDER', os.path.join(current_app.root_path, 'uploads', 'avatars'))
    return send_from_directory(avatar_dir, filename)


@main_bp.route('/dashboard/technician/delete-photo', methods=['POST'])
@login_required
def delete_technician_photo():
    """Allows technician to remove their current profile photo."""
    if not current_user.is_technician or not current_user.technician_profile:
        flash("Action non autorisée.", "danger")
        return redirect(url_for('main.dashboard'))

    profile = current_user.technician_profile
    if profile.photo_filename:
        avatar_dir = current_app.config.get('AVATAR_UPLOAD_FOLDER', os.path.join(current_app.root_path, 'uploads', 'avatars'))
        photo_path = os.path.join(avatar_dir, profile.photo_filename)
        if os.path.exists(photo_path):
            try:
                os.remove(photo_path)
            except OSError:
                pass
        profile.photo_filename = None
        db.session.commit()
        flash("Votre photo de profil a été supprimée.", "info")

    return redirect(url_for('main.technician_dashboard'))
