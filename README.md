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
├── Dockerfile                 # Configuration Docker production multi-stage avec utilisateur non-root
├── docker-compose.yml         # Orchestration complète Web (Flask/Gunicorn) + DB (PostgreSQL 16)
├── docker-entrypoint.sh       # Script de démarrage avec auto-seed et adaptation dynamique du port
├── .dockerignore              # Optimisation du contexte de build Docker
├── .env.example               # Modèle des variables d'environnement de production
├── app.py                     # Initialisation Flask, ProxyFix et gestionnaires d'erreurs
├── config.py                  # Configuration SQLite/PostgreSQL, pool de connexions et cookies sécurisés
├── models.py                  # Modèles SQLAlchemy (User, TechnicianProfile, RecruiterProfile)
├── routes.py                  # Routes Auth, Dashboard, Talents, API JSON, Healthcheck & Uploads
├── seed.py                    # Script de peuplement avec 6 techniciens marocains et 2 recruteurs
├── test_app.py                # Suite de 9 tests unitaires automatisés
├── requirements.txt           # Dépendances Python (Flask, Gunicorn, Psycopg2, SQLAlchemy)
├── README.md                  # Documentation technique et guides de déploiement Cloud
│
├── static/
│   ├── css/
│   │   └── custom.css         # Typographie, gradients industriels et scrollbar
│   └── js/
│       ├── main.js            # Menu mobile, auto-dismiss des alertes flash, tag picker
│       └── talents.js         # Filtrage en temps réel via Fetch API & tri dynamique
│
├── templates/
│   ├── base.html              # Layout principal avec favicon SVG, métadonnées SEO et navbar
│   ├── index.html             # Landing page avec Pôles marocains, Témoignages usines et FAQ
│   ├── talents.html           # Vivier des talents avec puces raccourcis et sélecteur de tri
│   ├── talent_detail.html     # Dossier complet du technicien (coordonnées directes / CV)
│   ├── dashboard.html         # Tableau de bord avec prévisualisation photo en direct
│   ├── login.html             # Page de connexion avec boutons de remplissage démo en 1 clic
│   ├── register.html          # Inscription avec sélecteur de rôle interactif
│   └── errors/
│       ├── 404.html           # Page d'erreur 404 brandée industrielle
│       ├── 500.html           # Page d'erreur 500 pour maintenance serveur
│       └── 413.html           # Page d'erreur 413 pour fichiers volumineux
│
└── uploads/
    ├── cvs/                   # Répertoire de stockage sécurisé des CVs
    └── avatars/               # Répertoire de stockage des photos de profil
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

## 🐳 Déploiement avec Docker & Docker Compose

L'application est conteneurisée et prête pour la production avec un serveur WSGI haute performance **Gunicorn (4 workers, 2 threads)** et une base de données **PostgreSQL 16**.

### 1. Lancement Local / Serveur en 1 Commande avec Docker Compose
```bash
docker compose up -d --build
```
L'application démarre automatiquement sur : **`http://localhost:5000`**
- Le service `db` (PostgreSQL 16) démarre avec volume persistant `postgres_data`.
- L'application Flask attend que la base de données soit saine (`service_healthy`).
- Le script `docker-entrypoint.sh` peuple automatiquement la base de données (`AUTO_SEED=true`) avec les 6 techniciens marocains et les comptes démo.
- Les CVs et photos de profil sont persistés dans le volume `uploads_data`.

Pour vérifier les logs :
```bash
docker compose logs -f web
```

Pour arrêter les services :
```bash
docker compose down
```

---

## ☁️ Déploiement chez les Fournisseurs Cloud

### 1. Déploiement Serverless sur Google Cloud Run
```bash
# Authentification et configuration du projet
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Build et push de l'image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/mainttech-jobs

# Déploiement instantané
gcloud run deploy mainttech-jobs \
  --image gcr.io/YOUR_PROJECT_ID/mainttech-jobs \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars "SECRET_KEY=votre_cle_secrete,AUTO_SEED=true,DATABASE_URL=postgresql://user:pass@host:5432/dbname"
```

### 2. Déploiement sur Render / Railway / Fly.io
1. Connectez votre dépôt GitHub à **Render** ou **Railway**.
2. Créez une base de données **PostgreSQL managée** en un clic.
3. Créez un nouveau **Web Service (Docker)** pointant sur le `Dockerfile`.
4. Ajoutez les variables d'environnement définies dans `.env.example` :
   - `DATABASE_URL` (fournie automatiquement par Render/Railway)
   - `SECRET_KEY`
   - `AUTO_SEED=true`
   - `PORT=5000` (ou valeur attribuée par la plateforme)
5. Le service est en ligne avec SSL automatique et healthcheck actif sur `/health`.

### 3. Déploiement sur AWS App Runner / ECS (Fargate)
1. Poussez l'image vers **Amazon ECR** :
   ```bash
   aws ecr get-login-password --region eu-west-3 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.eu-west-3.amazonaws.com
   docker build -t mainttech-jobs .
   docker tag mainttech-jobs:latest YOUR_ACCOUNT_ID.dkr.ecr.eu-west-3.amazonaws.com/mainttech-jobs:latest
   docker push YOUR_ACCOUNT_ID.dkr.ecr.eu-west-3.amazonaws.com/mainttech-jobs:latest
   ```
2. Créez un service **AWS App Runner** lié à l'image ECR.
3. Configurez le port `5000` et la sonde de santé sur `/health`.

---

## 🔍 Sonde de Santé Cloud (`/health`)

Pour surveiller l'état de l'application et de sa base de données (Kubernetes liveness/readiness probes, AWS ALB, Uptime Kuma) :
- `GET /health`
- Réponse `200 OK` :
  ```json
  {
    "database": "connected",
    "service": "mainttech-jobs-maroc",
    "status": "healthy"
  }
  ```
