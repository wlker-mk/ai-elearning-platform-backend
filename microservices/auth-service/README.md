# Auth Service - Django + Prisma

Service d'authentification et d'autorisation complet pour une plateforme d'apprentissage.

## 🚀 Fonctionnalités

### 🔐 Authentification
- **Inscription/Connexion** : Email + mot de passe
- **Vérification d'email** : Token de vérification avec email HTML
- **Réinitialisation de mot de passe** : Via email avec liens sécurisés
- **Changement de mot de passe** : Depuis le profil
- **Sessions sécurisées** : Gestion des sessions avec tokens Prisma
- **Refresh tokens** : Prolongation automatique des sessions

### 🛡️ Sécurité
- **Hash de mots de passe** : bcrypt avec 12 rounds
- **Politique de mot de passe** : Minimum 8 caractères, majuscules, minuscules, chiffres, caractères spéciaux
- **Verrouillage de compte** : Après 5 tentatives échouées (30 min)
- **Limitation de tentatives** : Protection contre brute force
- **IP tracking** : Suivi des connexions avec détection de localisation
- **User agent parsing** : Détection d'appareils et navigateurs
- **Alertes de sécurité** : Emails pour connexions suspectes

### 🔒 MFA (Multi-Factor Authentication)
- **TOTP** : Time-based One-Time Password (Google Authenticator, Authy)
- **QR Code** : Génération automatique pour configuration
- **Codes de backup** : 8 codes générés automatiquement
- **Désactivation sécurisée** : Avec vérification du mot de passe
- **Notification par email** : Alerte lors de l'activation

### 📊 Gestion des sessions
- **Sessions multiples** : Plusieurs appareils simultanés
- **Visualisation** : Liste de toutes les sessions actives avec détails
- **Révocation** : Déconnexion d'appareils spécifiques
- **Révocation globale** : Déconnexion de tous les appareils sauf actuel

### 📈 Historique & Analytics
- **Historique de connexion** : Toutes les tentatives (réussies et échouées)
- **Statistiques** : Taux de succès, appareils utilisés, pays
- **Alertes de sécurité** : Détection de connexions suspectes

### 👥 Rôles utilisateurs
- SUPER_ADMIN
- ADMIN
- MODERATOR
- INSTRUCTOR
- STUDENT
- STUDENT_PREMIUM
- TEACHING_ASSISTANT
- CONTENT_REVIEWER
- SUPPORT

## 📦 Installation

### Prérequis
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+ (pour Prisma)

### Installation locale

```bash
# 1. Cloner le repository
git clone <repo-url>
cd auth-service

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos valeurs

# 5. Générer le client Prisma
prisma generate

# 6. Exécuter les migrations
prisma migrate deploy
python manage.py migrate

# 7. Créer les dossiers nécessaires
mkdir -p logs static media

# 8. Lancer le serveur
python manage.py runserver 8001
```

### Installation avec Docker

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f auth-service

# Arrêter les services
docker-compose down

# Reconstruire après changements
docker-compose up -d --build
```

## 🧪 Tests

```bash
# Installer les dépendances de test
pip install pytest pytest-django pytest-asyncio pytest-cov

# Lancer tous les tests
pytest

# Lancer avec couverture
pytest --cov=apps --cov-report=html

# Lancer des tests spécifiques
pytest apps/authentication/tests/test_user_service.py
```

## 📚 Documentation API

### Health Check

**GET /api/auth/health/**
```json
{
  "status": "healthy",
  "service": "auth-service",
  "version": "1.0.0"
}
```

### Authentication

**POST /api/auth/register/**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "role": "STUDENT"
}
```

**POST /api/auth/login/**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "remember_me": true
}
```
Retourne:
- `requires_mfa: true` si MFA activé (nécessite `/login/mfa/`)
- Sinon: `access_token`, `refresh_token`, `user`

**POST /api/auth/login/mfa/**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "mfa_code": "123456"
}
```

**POST /api/auth/logout/**
Nécessite: Bearer Token

**POST /api/auth/refresh/**
```json
{
  "refresh_token": "your-refresh-token"
}
```

**POST /api/auth/verify-email/**
```json
{
  "token": "verification-token"
}
```

**POST /api/auth/password/request-reset/**
```json
{
  "email": "user@example.com"
}
```

**POST /api/auth/password/reset/**
```json
{
  "token": "reset-token",
  "new_password": "NewSecurePass123!",
  "new_password_confirm": "NewSecurePass123!"
}
```

**POST /api/auth/password/change/**
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewPass123!",
  "new_password_confirm": "NewPass123!"
}
```
Nécessite: Bearer Token

**GET /api/auth/me/**
Récupère les infos de l'utilisateur connecté
Nécessite: Bearer Token

### MFA

**POST /api/auth/mfa/enable/**
Initie l'activation du MFA
Retourne: secret, qr_code, backup_codes
Nécessite: Bearer Token

**POST /api/auth/mfa/verify/**
```json
{
  "code": "123456"
}
```
Nécessite: Bearer Token

**POST /api/auth/mfa/disable/**
```json
{
  "password": "YourPassword123!"
}
```
Nécessite: Bearer Token

**POST /api/auth/mfa/backup-codes/**
Régénère les codes de backup
Nécessite: Bearer Token

### Sessions

**GET /api/auth/sessions/**
Liste toutes les sessions actives
Nécessite: Bearer Token

**DELETE /api/auth/sessions/**
Révoque toutes les sessions sauf la courante
Nécessite: Bearer Token

**DELETE /api/auth/sessions/{session_id}/**
Révoque une session spécifique
Nécessite: Bearer Token

### Login History

**GET /api/auth/login-history/?limit=50&success_only=true**
Récupère l'historique de connexion
Nécessite: Bearer Token

**GET /api/auth/login-statistics/?days=30**
Récupère les statistiques de connexion
Nécessite: Bearer Token

## 🔒 Sécurité

### Password Requirements
- Minimum 8 caractères
- Au moins 1 majuscule
- Au moins 1 minuscule
- Au moins 1 chiffre
- Au moins 1 caractère spécial (!@#$%^&*()_+-=[]{}|;:,.<>?)

### Account Locking
- Verrouillage après 5 tentatives échouées
- Durée de verrouillage: 30 minutes
- Reset automatique après connexion réussie

### Session Security
- Durée de session: 24 heures
- Durée refresh token: 30 jours
- Révocation automatique des tokens expirés
- Tracking IP et User-Agent

### MFA
- TOTP avec fenêtre de 30 secondes
- Codes de backup à usage unique
- 8 codes générés par défaut
- Email de notification lors de l'activation

## 📧 Configuration Email

### Development (Console)
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Production (Gmail)
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Production (SendGrid, Mailgun, etc.)
Configurez selon votre fournisseur dans `.env`

## 💡 Exemples d'Utilisation

### 1. Inscription complète

```javascript
// 1. S'inscrire
const register = await fetch('/api/auth/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    username: 'johndoe',
    password: 'SecurePass123!',
    password_confirm: 'SecurePass123!'
  })
});

// 2. Vérifier l'email (lien envoyé par email)
const verify = await fetch('/api/auth/verify-email/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ token: 'verification-token' })
});

// 3. Se connecter
const login = await fetch('/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'SecurePass123!'
  })
});

const { access_token, refresh_token } = await login.json();
```

### 2. Activation MFA

```javascript
// 1. Initier l'activation
const enable = await fetch('/api/auth/mfa/enable/', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  }
});

const { qr_code, backup_codes } = await enable.json();

// 2. Afficher le QR code à l'utilisateur
// Sauvegarder les backup_codes

// 3. Vérifier avec un code de l'app
const verify = await fetch('/api/auth/mfa/verify/', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ code: '123456' })
});
```

### 3. Gestion des sessions

```javascript
// Voir toutes les sessions actives
const sessions = await fetch('/api/auth/sessions/', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});

// Révoquer une session spécifique
await fetch(`/api/auth/sessions/${session_id}/`, {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${access_token}` }
});

// Déconnexion de tous les appareils sauf le courant
await fetch('/api/auth/sessions/', {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

## 🎯 Points clés

1. **Zero Trust** : Vérification à chaque requête
2. **Stateless** : Pas de sessions Django, tout en Prisma
3. **Scalable** : Supporte des millions d'utilisateurs
4. **Secure by default** : Toutes les best practices implémentées
5. **Auditable** : Historique complet de toutes les actions
6. **Production-ready** : Tests, logging, monitoring

## 🐛 Debugging

```bash
# Voir les logs
tail -f logs/app.log
tail -f logs/error.log

# Logs Docker
docker-compose logs -f auth-service

# Shell Prisma
prisma studio

# Shell Django
python manage.py shell
```

## 🔄 Migrations

```bash
# Créer une migration Prisma
prisma migrate dev --name migration_name

# Appliquer en production
prisma migrate deploy

# Générer le client
prisma generate
```

## 📝 Licence

MIT

## 📞 Support

Pour toute question ou problème, ouvrez une issue sur GitHub.

# Ajouter à requirements.txt pour OAuth

# ==========================================
# OAUTH & HTTP CLIENTS
# ==========================================
httpx==0.25.2
authlib==1.3.0
python-jose[cryptography]==3.3.0 # Pour JWT
requests-oauthlib==1.3.1
oauthlib==3.2.0
pyjwt[crypto]==2.6.0 # Pour JWT
```