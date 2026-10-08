# 🏭 MaintTech Jobs Maroc

**Plateforme B2B de recrutement spécialisée pour les Techniciens de Maintenance Industrielle au Maroc**  
*(Écosystème Automobile, Aéronautique, Agroalimentaire, Textile, Chimie & OCP)*

---

## 📌 Présentation du Projet

**MaintTech Jobs** transforme le sourcing de compétences industrielles en connectant directement les recruteurs d'usines (Tanger Med, Atlantic Free Zone Kénitra, Midparc Nouaceur, Berrechid, Jorf Lasfar) avec des techniciens d'élite en :
- **Automatisme & Robotique** (Siemens TIA Portal, S7-1500, KUKA KRC4, Fanuc, WinCC)
- **Électromécanique & Variateurs** (Schneider Altivar, Lexium, armoires de distribution)
- **Maintenance Mécanique** (Lignage laser, pompes centrifuges, réducteurs SEW)
- **Hydraulique & Pneumatique** (Festo, Parker, circuits haute pression 350 bars)
- **Machines Spéciales & CNC** (Fanuc 0i, Heidenhain TNC, tables de découpe Lectra Vector)

---

## 🏗️ Architecture & Stack Technique

- **Backend** : Python 3.11+ avec **Flask 3.1**
- **Base de Données** : **SQLAlchemy 2.0 / Flask-SQLAlchemy**
  - Configurée pour fonctionner nativement sur **SQLite** en local (`mainttech.db`).
  - Prête pour le passage transparent vers **PostgreSQL** en production via la variable d'environnement `DATABASE_URL` (compatible Supabase, Neon, Render, Railway, AWS RDS).
- **Authentification & Sécurité** : **Flask-Login** & **Werkzeug Security** (hachage sécurisé des mots de passe avec `generate_password_hash`).
- **Frontend & Rendu** : **Jinja2**, HTML5, CSS3 avec **Tailwind CSS**, Font Awesome 6.
- **Moteur de Recherche Dynamique** : **Vanilla JavaScript** & **Fetch API** avec debouncing (300ms) pour filtrage en temps réel sans rechargement de page.
- **Gestion des Fichiers** : Téléversement et téléchargement sécurisé des CVs avec vérification des extensions (`.pdf`, `.doc`, `.docx`) et protection d'accès aux recruteurs certifiés.

---

## 📁 Structure du Projet

```
test-anti/
│
├── app.py                     # Initialisation de l'application Flask et extensions
├── config.py                  # Configuration SQLite / PostgreSQL, uploads et secrets
├── models.py                  # Modèles SQLAlchemy (User, TechnicianProfile, RecruiterProfile)
├── routes.py                  # Routes Auth, Dashboard, Vivier des Talents, API JSON et Téléchargement CV
├── seed.py                    # Script de peuplement avec 6 techniciens marocains et 2 recruteurs
├── test_app.py                # Suite de tests unitaires automatisés
├── requirements.txt           # Dépendances Python
├── README.md                  # Documentation technique et guide d'exécution
│
├── static/
│   ├── css/
│   │   └── custom.css         # Typographie, gradients industriels et scrollbar
│   └── js/
│       ├── main.js            # Menu mobile, auto-dismiss des alertes flash, tag picker
│       └── talents.js         # Filtrage en temps réel via Fetch API & rendu dynamique des cartes
│
├── templates/
│   ├── base.html              # Layout principal avec Navbar réactive, alertes et footer
│   ├── index.html             # Page d'accueil avec Pôles marocains et top 3 talents dynamiques
│   ├── talents.html           # Vivier des talents avec panneau de filtres et grille dynamique
│   ├── talent_detail.html     # Dossier complet du technicien (coordonnées directes / téléchargement CV)
│   ├── dashboard.html         # Tableau de bord adaptatif (Technicien ou Recruteur)
│   ├── login.html             # Page de connexion avec boutons de remplissage démo en 1 clic
│   └── register.html          # Inscription avec sélecteur de rôle interactif (Technicien vs Recruteur)
│
└── uploads/
    └── cvs/                   # Répertoire de stockage sécurisé des CVs
```

---

## 🗄️ Schéma de Base de Données

### 1. `User`
- `id` (PK)
- `email` (Unique, String)
- `password_hash` (String 256)
- `role` ('technician' ou 'recruiter')
- `created_at` (DateTime)
- Relations 1-à-1 : `technician_profile`, `recruiter_profile`

### 2. `TechnicianProfile`
- `id` (PK)
- `user_id` (FK -> `users.id`, Unique)
- `full_name` (String)
- `phone` (String, direct WhatsApp)
- `city` (Casablanca, Tanger, Kénitra, Meknès, Fès, Jorf Lasfar...)
- `specialty` (Electromécanique, Automatisme, Maintenance Mécanique, Hydraulique/Pneumatique, CNC, Lectra...)
- `skills` (JSON array des automates et technologies)
- `experience_years` (Integer)
- `mobility` (Boolean : mobile sur tout le Maroc)
- `cv_filename` (String : nom sécurisé du fichier sur le serveur)
- `photo_filename` (String : photo de profil professionnelle)
- `bio` (Text)

### 3. `RecruiterProfile`
- `id` (PK)
- `user_id` (FK -> `users.id`, Unique)
- `company_name` (String)
- `industry_type` (Automobile, Aéronautique, Agroalimentaire, Textile, Chimie...)
- `city` (String)
- `phone` (String)

---

## 🚀 Démarrage Rapide

### 1. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 2. Initialisation et Amorçage de la Base de Données
Exécutez le script d'amorce pour créer les tables SQLite et injecter les 6 profils marocains réalistes ainsi que les comptes démo :
```bash
python seed.py
```

### 3. Lancement du Serveur de Développement
```bash
python app.py
```
L'application est disponible sur : **`http://127.0.0.1:5000`**

### 4. Exécution de la Suite de Tests
```bash
python -m unittest test_app.py
```

---

## 🔑 Comptes de Démonstration (Test Immédiat)

Pour faciliter vos tests, la page de connexion (`/login`) dispose de **boutons en 1-clic** qui remplissent automatiquement ces identifiants :

| Rôle | Adresse Email | Mot de Passe | Détails & Localisation |
| :--- | :--- | :--- | :--- |
| **Recruteur Démo** | `recruteur@renault-tanger.ma` | `Password123!` | Renault Group Maroc - Usine Tanger Med (Accès complet aux téléphones et téléchargement des CVs) |
| **Technicien Démo** | `karim.alami@mainttech.ma` | `Password123!` | Karim Alami - Casablanca (Électromécanicien Senior, Siemens TIA Portal, 6 ans d'expérience) |

---

## 🌐 Endpoints & API

- `GET /` : Landing page avec statistiques industrielles et top 3 profils en vedette.
- `GET /talents` : Vivier des talents avec filtres multi-critères.
- `GET /api/talents` : Endpoint JSON pour le filtrage direct en JavaScript (Fetch API).
  - Paramètres supportés : `?city=Tanger&specialty=Automatisme&min_exp=5&search=Siemens&mobility=true`
- `GET /talents/<id>` : Dossier complet du technicien.
- `GET /download/cv/<id>` : Téléchargement du CV (sécurisé, réservé aux recruteurs connectés).
- `GET /dashboard` : Tableau de bord adaptatif selon le rôle de l'utilisateur connecté.
- `GET/POST /register` : Inscription avec sélection interactive du rôle.
- `GET/POST /login` : Connexion session avec option "Se souvenir de moi".
- `GET /logout` : Déconnexion.

---

## 🔄 Passage en Production (PostgreSQL)

Pour basculer de SQLite vers PostgreSQL en production :
1. Définissez la variable d'environnement `DATABASE_URL` :
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/mainttech_prod"
   ```
2. Installez `psycopg2-binary` :
   ```bash
   pip install psycopg2-binary
   ```
3. L'application détecte automatiquement PostgreSQL et gère les préfixes `postgres://` et `postgresql://`.
