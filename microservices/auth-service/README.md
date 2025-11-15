"""
# Auth Service - Django + Prisma

Service d'authentification et d'autorisation complet pour une plateforme d'apprentissage.

## 🚀 Fonctionnalités

### 🔐 Authentification
- **Inscription/Connexion** : Email + mot de passe
- **Vérification d'email** : Token de vérification
- **Réinitialisation de mot de passe** : Via email
- **Changement de mot de passe** : Depuis le profil
- **Sessions sécurisées** : Gestion des sessions avec tokens
- **Refresh tokens** : Prolongation automatique des sessions

### 🛡️ Sécurité
- **Hash de mots de passe** : bcrypt avec salt
- **Politique de mot de passe** : Minimum 8 caractères, majuscules, minuscules, chiffres, caractères spéciaux
- **Verrouillage de compte** : Après 5 tentatives échouées
- **Limitation de tentatives** : Protection contre brute force
- **IP tracking** : Suivi des connexions
- **User agent tracking** : Détection d'appareils

### 🔒 MFA (Multi-Factor Authentication)
- **TOTP** : Time-based One-Time Password (Google Authenticator, Authy)
- **QR Code** : Génération automatique pour configuration
- **Codes de backup** : 8 codes générés automatiquement
- **Désactivation sécurisée** : Avec vérification du mot de passe

### 📊 Gestion des sessions
- **Sessions multiples** : Plusieurs appareils simultanés
- **Visualisation** : Liste de toutes les sessions actives
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

### 🌐 Providers OAuth (prévu)
- Google
- GitHub
- Facebook
- LinkedIn
- Microsoft
- Apple
- SSO Enterprise
- SAML

## 📦 Installation

### Prérequis
- Python 3.11+
- PostgreSQL 15+
- Node.js 18+ (pour Prisma)

### Installation locale

```bash
# 1. Cloner le repository
git clone <repo-url>
cd auth-service

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate

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

# 7. Lancer le serveur
python manage.py runserver 8002
```

### Installation avec Docker

```bash
docker-compose up -d
```

## 📚 Documentation API

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

**GET /api/auth/me/**
Récupère les infos de l'utilisateur connecté

### MFA

**POST /api/auth/mfa/enable/**
Initie l'activation du MFA
Retourne: secret, qr_code, backup_codes

**POST /api/auth/mfa/verify/**
```json
{
  "code": "123456"
}
```

**POST /api/auth/mfa/disable/**
```json
{
  "password": "YourPassword123!"
}
```

**POST /api/auth/mfa/backup-codes/**
Régénère les codes de backup

### Sessions

**GET /api/auth/sessions/**
Liste toutes les sessions actives

**DELETE /api/auth/sessions/**
Révoque toutes les sessions sauf la courante

**DELETE /api/auth/sessions/{session_id}/**
Révoque une session spécifique

### Login History

**GET /api/auth/login-history/?limit=50&success_only=true**
Récupère l'historique de connexion

**GET /api/auth/login-statistics/?days=30**
Récupère les statistiques de connexion

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

### MFA
- TOTP avec fenêtre de 30 secondes
- Codes de backup à usage unique
- 8 codes générés par défaut

## 💡 Cas d'usage

### 1. Inscription complète

```javascript
// 1. S'inscrire
const register = await fetch('/api/auth/register/', {
  method: 'POST',
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
  body: JSON.stringify({ token: 'verification-token' })
});

// 3. Se connecter
const login = await fetch('/api/auth/login/', {
  method: 'POST',
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'SecurePass123!'
  })
});
```

### 2. Activation MFA

```javascript
// 1. Initier l'activation
const enable = await fetch('/api/auth/mfa/enable/', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer your-token' }
});

// Afficher le QR code à l'utilisateur
const { qr_code, backup_codes } = enable.data;

// 2. Vérifier avec un code de l'app
const verify = await fetch('/api/auth/mfa/verify/', {
  method: 'POST',
  body: JSON.stringify({ code: '123456' }),
  headers: { 'Authorization': 'Bearer your-token' }
});

// 3. Sauvegarder les backup codes
saveBackupCodes(backup_codes);
```

### 3. Gestion des sessions

```javascript
// Voir toutes les sessions actives
const sessions = await fetch('/api/auth/sessions/', {
  headers: { 'Authorization': 'Bearer your-token' }
});

// Révoquer une session spécifique
await fetch(`/api/auth/sessions/${session_id}/`, {
  method: 'DELETE',
  headers: { 'Authorization': 'Bearer your-token' }
});

// Déconnexion de tous les appareils sauf le courant
await fetch('/api/auth/sessions/', {
  method: 'DELETE',
  headers: { 'Authorization': 'Bearer your-token' }
});
```

## 🎯 Points clés

1. **Zero Trust** : Vérification à chaque requête
2. **Stateless** : Pas de sessions Django, tout en Prisma
3. **Scalable** : Supporte des millions d'utilisateurs
4. **Secure by default** : Toutes les best practices implémentées
5. **Auditable** : Historique complet de toutes les actions

## 📝 Licence

MIT
"""
## Endpoints disponibles :
# Authentication
POST   /api/auth/register/
POST   /api/auth/login/
POST   /api/auth/login/mfa/
POST   /api/auth/logout/
POST   /api/auth/refresh/
POST   /api/auth/verify-email/
POST   /api/auth/password/request-reset/
POST   /api/auth/password/reset/
POST   /api/auth/password/change/
GET    /api/auth/me/

# MFA
POST   /api/auth/mfa/enable/
POST   /api/auth/mfa/verify/
POST   /api/auth/mfa/disable/
POST   /api/auth/mfa/backup-codes/

# Sessions
GET    /api/auth/sessions/
DELETE /api/auth/sessions/
DELETE /api/auth/sessions/{session_id}/

# Login History
GET    /api/auth/login-history/
GET    /api/auth/login-statistics/