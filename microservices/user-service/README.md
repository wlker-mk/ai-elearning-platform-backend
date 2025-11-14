"""
# User Service - Django + Prisma

Service de gestion des utilisateurs pour une plateforme d'apprentissage en ligne.

## 🚀 Fonctionnalités

### Profils Utilisateurs
- Création et gestion de profils complets
- Informations personnelles (nom, email, téléphone, etc.)
- Photos de profil et bannière
- Liens réseaux sociaux
- Préférences (langue, timezone, devise)

### Étudiants
- Profil étudiant avec code unique
- Système de points et niveaux (gamification)
- Suivi du streak d'activité
- Statistiques d'apprentissage
- Classement (leaderboard)
- Catégories préférées

### Instructeurs
- Profil instructeur avec code unique
- Spécialisations et expertise
- Certifications
- Taux horaire
- Système de notation
- Vérification des instructeurs
- Statistiques (étudiants, cours, notes)

## 📦 Installation

### Prérequis
- Python 3.11+
- PostgreSQL 15+
- Node.js 18+ (pour Prisma)

### Installation locale

1. Cloner le repository
```bash
git clone <repo-url>
cd user-service
```

2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement
```bash
cp .env.example .env
# Éditer .env avec vos valeurs
```

5. Générer le client Prisma
```bash
prisma generate
```

6. Exécuter les migrations
```bash
prisma migrate deploy
python manage.py migrate
```

7. Créer un superuser
```bash
python manage.py createsuperuser
```

8. Lancer le serveur
```bash
python manage.py runserver
```

### Installation avec Docker

```bash
docker-compose up -d
```

## 🧪 Tests

Lancer tous les tests :
```bash
python manage.py test
```

Lancer les tests d'une app spécifique :
```bash
python manage.py test apps.users.tests.test_profiles
```

Avec coverage :
```bash
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📚 Documentation API

### Profils

**GET /api/users/profiles/me/**
- Récupérer son profil

**POST /api/users/profiles/me/**
- Créer son profil
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "country": "USA",
  "city": "New York"
}
```

**PUT /api/users/profiles/me/**
- Mettre à jour son profil

**GET /api/users/profiles/{user_id}/**
- Récupérer un profil public

### Étudiants

**GET /api/users/students/me/**
- Récupérer son profil étudiant

**POST /api/users/students/me/**
- Créer son profil étudiant

**POST /api/users/students/experience/**
- Ajouter de l'expérience
```json
{
  "points": 150
}
```

**POST /api/users/students/streak/**
- Mettre à jour le streak d'activité

**GET /api/users/students/leaderboard/?limit=10**
- Récupérer le classement

### Instructeurs

**GET /api/users/instructors/me/**
- Récupérer son profil instructeur

**POST /api/users/instructors/me/**
- Créer son profil instructeur

**GET /api/users/instructors/{user_id}/**
- Récupérer un profil instructeur public

**GET /api/users/instructors/top/?limit=10**
- Récupérer les meilleurs instructeurs

**GET /api/users/instructors/search/**
- Rechercher des instructeurs
- Paramètres : `specialization`, `min_rating`, `verified_only`, `limit`

## 🏗️ Architecture

```
user-service/
├── apps/
│   └── users/
│       ├── profiles/      # Gestion des profils
│       ├── students/      # Gestion des étudiants
│       └── instructors/   # Gestion des instructeurs
├── config/                # Configuration Django
├── shared/                # Utilitaires partagés
├── prisma/                # Schéma et migrations Prisma
└── tests/                 # Tests
```

## 🔐 Sécurité

- Authentification JWT
- Validation des données
- Protection CSRF
- CORS configuré
- Sanitization des entrées
- Rate limiting (à implémenter)

## 📝 Licence

MIT

## 👥 Auteurs

Votre équipe de développement
"""