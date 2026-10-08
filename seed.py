import os
import sys
from app import create_app
from models import db, User, TechnicianProfile, RecruiterProfile

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def seed_database():
    """
    Populates the database with 6 realistic Moroccan industrial maintenance technicians
    and 2 industrial recruiters for immediate demonstration and testing.
    """
    app = create_app()

    with app.app_context():
        print("[*] Resetting and recreating database tables...")
        db.drop_all()
        db.create_all()

        upload_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)

        # ----------------------------------------------------
        # 1. SEED RECRUITERS
        # ----------------------------------------------------
        recruiters_data = [
            {
                "email": "recruteur@renault-tanger.ma",
                "password": "Password123!",
                "company_name": "Renault Group Maroc (Usine Tanger Med)",
                "industry_type": "Automobile",
                "city": "Tanger",
                "phone": "+212 5 39 39 40 00"
            },
            {
                "email": "rh@midparc-aero.ma",
                "password": "Password123!",
                "company_name": "Hexcel Composites Midparc",
                "industry_type": "Aéronautique",
                "city": "Casablanca",
                "phone": "+212 5 22 53 80 00"
            }
        ]

        print("[*] Seeding Industrial Recruiters...")
        for r in recruiters_data:
            user = User(email=r["email"], role="recruiter")
            user.set_password(r["password"])
            db.session.add(user)
            db.session.flush()

            recruiter = RecruiterProfile(
                user_id=user.id,
                company_name=r["company_name"],
                industry_type=r["industry_type"],
                city=r["city"],
                phone=r["phone"]
            )
            db.session.add(recruiter)

        # ----------------------------------------------------
        # 2. SEED TECHNICIANS
        # ----------------------------------------------------
        technicians_data = [
            {
                "email": "karim.alami@mainttech.ma",
                "password": "Password123!",
                "full_name": "Karim Alami",
                "phone": "+212 6 61 12 34 56",
                "city": "Casablanca",
                "specialty": "Electromécanique",
                "experience_years": 6,
                "mobility": True,
                "skills": [
                    "Siemens TIA Portal",
                    "Schneider Altivar VFD",
                    "Festo Pneumatique",
                    "GMAO Coswin",
                    "Lecture de Schémas Électriques"
                ],
                "bio": "Technicien supérieur en électromécanique avec 6 ans d'expérience dans les parcs industriels de Casablanca (Midparc, Bouskoura). Spécialiste du diagnostic d'armoires d'automatisme, de l'alignement des moteurs électriques et du dépannage de variateurs de vitesse.",
                "cv_file": "CV_Karim_Alami_Electromecanique.pdf"
            },
            {
                "email": "youssef.benjelloun@mainttech.ma",
                "password": "Password123!",
                "full_name": "Youssef Benjelloun",
                "phone": "+212 6 62 88 99 00",
                "city": "Tanger",
                "specialty": "Automatisme",
                "experience_years": 8,
                "mobility": True,
                "skills": [
                    "Siemens TIA Portal (S7-1500)",
                    "Schneider VFD",
                    "Robotique KUKA",
                    "Robotique Fanuc",
                    "Profinet / Modbus TCP",
                    "Supervision WinCC"
                ],
                "bio": "Automaticien senior certifié Siemens TIA Portal avec 8 ans d'expérience au sein de Tanger Automotive City (TAC). Intervention sur îlots robotisés KUKA et Fanuc, mise en service de lignes automatisées et optimisation du temps de cycle usine.",
                "cv_file": "CV_Youssef_Benjelloun_Automatisme.pdf"
            },
            {
                "email": "amine.tazi@mainttech.ma",
                "password": "Password123!",
                "full_name": "Amine Tazi",
                "phone": "+212 6 63 45 67 89",
                "city": "Kénitra",
                "specialty": "Maintenance Mécanique",
                "experience_years": 4,
                "mobility": True,
                "skills": [
                    "Alignement Laser",
                    "Pompes Centrifuges",
                    "Réducteurs SEW-Eurodrive",
                    "Hydraulique Bosch Rexroth",
                    "Maintenance Prédictive Vibratoire"
                ],
                "bio": "Technicien mécanique basé à Kénitra (Atlantic Free Zone). Expertise sur presses industrielles, réducteurs mécaniques et pompes d'alimentation. Pratique quotidienne des contrôles géométriques et lignages laser.",
                "cv_file": "CV_Amine_Tazi_Mecanique.pdf"
            },
            {
                "email": "hassan.idrissi@mainttech.ma",
                "password": "Password123!",
                "full_name": "Hassan El Idrissi",
                "phone": "+212 6 65 77 11 22",
                "city": "Meknès",
                "specialty": "Hydraulique/Pneumatique",
                "experience_years": 9,
                "mobility": False,
                "skills": [
                    "Festo Pneumatique",
                    "Centrales Hydrauliques Parker",
                    "Distributeurs Proportionnels",
                    "Compresseurs Atlas Copco",
                    "Vérins Hydrauliques Haute Pression"
                ],
                "bio": "Chef d'équipe maintenance fluides industriels à Meknès. 9 années d'expertise dans l'industrie agroalimentaire et le packaging. Maîtrise des circuits de puissance hydraulique jusqu'à 350 bars et des réseaux pneumatiques Festo.",
                "cv_file": "CV_Hassan_El_Idrissi_Hydraulique.pdf"
            },
            {
                "email": "mehdi.chraibi@mainttech.ma",
                "password": "Password123!",
                "full_name": "Mehdi Chraibi",
                "phone": "+212 6 66 33 44 55",
                "city": "Casablanca",
                "specialty": "Découpe Automatique (Lectra)",
                "experience_years": 5,
                "mobility": True,
                "skills": [
                    "Lectra Vector (Q80/iX6)",
                    "Schneider VFD (Lexium)",
                    "Servomoteurs Haute Précision",
                    "Festo Pneumatique",
                    "Calibrage Têtes de Coupe"
                ],
                "bio": "Technicien spécialiste machines spéciales et découpe automatique Lectra Vector dans le secteur textile technique et sellerie automobile. Maintenance électronique des variateurs brushless et dépannage mécanique de haute précision.",
                "cv_file": "CV_Mehdi_Chraibi_Lectra.pdf"
            },
            {
                "email": "omar.berrada@mainttech.ma",
                "password": "Password123!",
                "full_name": "Omar Berrada",
                "phone": "+212 6 68 22 33 44",
                "city": "Jorf Lasfar",
                "specialty": "CNC",
                "experience_years": 7,
                "mobility": True,
                "skills": [
                    "CNC Fanuc (0i/31i)",
                    "Heidenhain TNC",
                    "Siemens Sinamics VFD",
                    "Omron Sysmac",
                    "GMAO SAP PM"
                ],
                "bio": "Technicien de maintenance MOCN (Machines-Outils à Commande Numérique) intervenant sur le complexe industriel de Jorf Lasfar. Diagnostic approfondi des axes numériques, règles de mesure optiques et variateurs de broche.",
                "cv_file": "CV_Omar_Berrada_CNC.pdf"
            }
        ]

        print("[*] Seeding Moroccan Maintenance Technicians...")
        for t in technicians_data:
            user = User(email=t["email"], role="technician")
            user.set_password(t["password"])
            db.session.add(user)
            db.session.flush()

            # Create a sample dummy CV file so CV downloads work out of the box
            cv_path = os.path.join(upload_dir, t["cv_file"])
            if not os.path.exists(cv_path):
                with open(cv_path, "w", encoding="utf-8") as f:
                    f.write(f"--- CURRICULUM VITAE PROFESSIONNEL ---\n")
                    f.write(f"Nom: {t['full_name']}\n")
                    f.write(f"Spécialité: {t['specialty']}\n")
                    f.write(f"Ville: {t['city']} (Maroc)\n")
                    f.write(f"Expérience: {t['experience_years']} ans\n")
                    f.write(f"Compétences clés: {', '.join(t['skills'])}\n\n")
                    f.write(f"Profil:\n{t['bio']}\n")

            profile = TechnicianProfile(
                user_id=user.id,
                full_name=t["full_name"],
                phone=t["phone"],
                city=t["city"],
                specialty=t["specialty"],
                experience_years=t["experience_years"],
                mobility=t["mobility"],
                cv_filename=t["cv_file"],
                bio=t["bio"]
            )
            profile.set_skills(t["skills"])
            db.session.add(profile)

        db.session.commit()
        print("[OK] Database successfully seeded with 6 Technicians and 2 Recruiters!")
        print("\n---------------- DEMO LOGIN ACCOUNTS ----------------")
        print("[Recruiter Account]")
        print("   Email:    recruteur@renault-tanger.ma")
        print("   Password: Password123!")
        print("\n[Technician Account]")
        print("   Email:    karim.alami@mainttech.ma")
        print("   Password: Password123!")
        print("-----------------------------------------------------")

if __name__ == '__main__':
    seed_database()
