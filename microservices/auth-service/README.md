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


# 🔐 Documentation API - Auth Service

**Base URL:** `http://localhost:8001/api/auth/`

---

## 📌 AUTHENTIFICATION DE BASE

### 1. Inscription
```http
POST http://localhost:8001/api/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "role": "STUDENT"  // Optionnel: STUDENT (défaut) | INSTRUCTOR
}

RÉPONSE 201 CREATED:
{
  "user": {
    "id": "uuid",
    "username": "johndoe",
    "email": "user@example.com",
    "role": "STUDENT",
    "is_email_verified": false,
    "is_active": true,
    "mfa_enabled": false,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "Registration successful. Please verify your email."
}
```

### 2. Vérification d'Email
```http
POST /api/auth/verify-email/
Content-Type: application/json

{
  "token": "verification-token-from-email"
}

RÉPONSE 200 OK:
{
  "message": "Email verified successfully"
}
```

### 3. Connexion (sans MFA)
```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "remember_me": true  // Optionnel
}

RÉPONSE 200 OK:
{
  "user": { /* ... */ },
  "access_token": "session-token-xyz",
  "refresh_token": "refresh-token-abc",
  "expires_at": "2024-01-02T00:00:00Z",
  "message": "Login successful"
}

RÉPONSE 428 (Si MFA activé):
{
  "requires_mfa": true,
  "user_id": "uuid",
  "message": "MFA code required"
}
```

### 4. Connexion avec MFA
```http
POST /api/auth/login/mfa/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "mfa_code": "123456"
}

RÉPONSE 200 OK:
{
  "user": { /* ... */ },
  "access_token": "session-token-xyz",
  "refresh_token": "refresh-token-abc",
  "expires_at": "2024-01-02T00:00:00Z",
  "message": "Login successful"
}
```

### 5. Déconnexion
```http
POST /api/auth/logout/
Authorization: Bearer {access_token}

RÉPONSE 200 OK:
{
  "message": "Logout successful"
}
```

### 6. Rafraîchir le Token
```http
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh_token": "refresh-token-abc"
}

RÉPONSE 200 OK:
{
  "session_token": "new-session-token",
  "refresh_token": "new-refresh-token",
  "expires_at": "2024-01-02T00:00:00Z"
}
```

---

## 🔑 GESTION DU MOT DE PASSE

### 7. Demander Réinitialisation
```http
POST /api/auth/password/request-reset/
Content-Type: application/json

{
  "email": "user@example.com"
}

RÉPONSE 200 OK:
{
  "message": "If the email exists, a reset link has been sent"
}
```

### 8. Réinitialiser le Mot de Passe
```http
POST /api/auth/password/reset/
Content-Type: application/json

{
  "token": "reset-token-from-email",
  "new_password": "NewSecurePass123!",
  "new_password_confirm": "NewSecurePass123!"
}

RÉPONSE 200 OK:
{
  "message": "Password reset successful"
}
```

### 9. Changer le Mot de Passe (connecté)
```http
POST /api/auth/password/change/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "current_password": "OldPass123!",
  "new_password": "NewPass123!",
  "new_password_confirm": "NewPass123!"
}

RÉPONSE 200 OK:
{
  "message": "Password changed successfully"
}
```

---

## 🔒 AUTHENTIFICATION À DEUX FACTEURS (MFA)

### 10. Activer MFA (Étape 1)
```http
POST /api/auth/mfa/enable/
Authorization: Bearer {access_token}

RÉPONSE 200 OK:
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,...",
  "backup_codes": [
    "1234-5678",
    "8765-4321",
    // ... 6 autres codes
  ],
  "message": "Scan the QR code with your authenticator app and verify with a code"
}
```

**Instructions pour le Frontend:**
1. Afficher le QR code à l'utilisateur
2. Sauvegarder les `backup_codes` (afficher avec option de téléchargement)
3. Demander à l'utilisateur de scanner avec Google Authenticator / Authy
4. Passer à l'étape 2

### 11. Vérifier et Activer MFA (Étape 2)
```http
POST /api/auth/mfa/verify/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "code": "123456"  // Code de l'app authenticator
}

RÉPONSE 200 OK:
{
  "message": "MFA activated successfully"
}
```

### 12. Désactiver MFA
```http
POST /api/auth/mfa/disable/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "password": "YourPassword123!"
}

RÉPONSE 200 OK:
{
  "message": "MFA disabled successfully"
}
```

### 13. Régénérer Codes de Backup
```http
POST /api/auth/mfa/backup-codes/
Authorization: Bearer {access_token}

RÉPONSE 200 OK:
{
  "backup_codes": [
    "1234-5678",
    "8765-4321",
    // ... 6 autres codes
  ],
  "message": "Backup codes regenerated successfully"
}
```

---

## 🌐 OAUTH (GOOGLE & GITHUB)

### 14. Connexion Google
```http
POST /api/auth/oauth/google/
Content-Type: application/json

{
  "code": "google-authorization-code",
  "redirect_uri": "http://localhost:3000/auth/google/callback"
}

RÉPONSE 200 OK:
{
  "user": { /* ... */ },
  "access_token": "session-token",
  "refresh_token": "refresh-token",
  "expires_at": "2024-01-02T00:00:00Z",
  "is_new_user": true,  // true si nouveau compte créé
  "message": "Google authentication successful"
}
```

**Instructions OAuth Google:**
1. Frontend redirige vers: `https://accounts.google.com/o/oauth2/v2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:3000/auth/google/callback&response_type=code&scope=email%20profile`
2. Google redirige vers votre callback avec `?code=...`
3. Envoyez ce code à `/api/auth/oauth/google/`

### 15. Connexion GitHub
```http
POST /api/auth/oauth/github/
Content-Type: application/json

{
  "code": "github-authorization-code"
}

RÉPONSE 200 OK:
{
  "user": { /* ... */ },
  "access_token": "session-token",
  "refresh_token": "refresh-token",
  "expires_at": "2024-01-02T00:00:00Z",
  "is_new_user": false,
  "message": "GitHub authentication successful"
}
```

**Instructions OAuth GitHub:**
1. Frontend redirige vers: `https://github.com/login/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:3000/auth/github/callback&scope=user:email`
2. GitHub redirige vers votre callback avec `?code=...`
3. Envoyez ce code à `/api/auth/oauth/github/`

### 16. Lier un Compte OAuth
```http
POST /api/auth/oauth/link/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "provider": "GOOGLE",  // ou "GITHUB"
  "code": "oauth-code",
  "redirect_uri": "http://localhost:3000/callback"  // Pour Google seulement
}

RÉPONSE 200 OK:
{
  "message": "GOOGLE account linked successfully"
}
```

### 17. Délier un Compte OAuth
```http
POST /api/auth/oauth/unlink/
Authorization: Bearer {access_token}

RÉPONSE 200 OK:
{
  "message": "OAuth provider unlinked successfully"
}
```

---

## 👤 PROFIL UTILISATEUR

### 18. Obtenir Profil Actuel
```http
GET /api/auth/me/
Authorization: Bearer {access_token}

RÉPONSE 200 OK:
{
  "id": "uuid",
  "username": "johndoe",
  "email": "user@example.com",
  "role": "STUDENT",
  "is_email_verified": true,
  "is_active": true,
  "is_suspended": false,
  "mfa_enabled": true,
  "last_login_at": "2024-01-01T10:30:00Z",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## 🖥️ GESTION DES SESSIONS

### 19. Lister les Sessions Actives
```http
GET /api/auth/sessions/
Authorization: Bearer {access_token}

RÉPONSE 200 OK:
[
  {
    "id": "uuid",
    "token": "session-token-xxx",
    "expires_at": "2024-01-02T00:00:00Z",
    "ip_address": "192.168.1.1",
    "device": "Desktop",
    "created_at": "2024-01-01T00:00:00Z"
  },
  // ... autres sessions
]
```

### 20. Révoquer une Session Spécifique
```http
DELETE /api/auth/sessions/{session_id}/
Authorization: Bearer {access_token}

RÉPONSE 200 OK:
{
  "message": "Session revoked successfully"
}
```

### 21. Révoquer Toutes les Sessions (sauf actuelle)
```http
DELETE /api/auth/sessions/
Authorization: Bearer {access_token}

RÉPONSE 200 OK:
{
  "message": "3 sessions revoked successfully"
}
```

---

## 📊 HISTORIQUE & STATISTIQUES

### 22. Historique de Connexion
```http
GET /api/auth/login-history/?limit=50&success_only=true
Authorization: Bearer {access_token}

RÉPONSE 200 OK:
[
  {
    "id": "uuid",
    "success": true,
    "failure_reason": null,
    "ip_address": "192.168.1.1",
    "location": "Paris, France",
    "country": "France",
    "city": "Paris",
    "device": "Desktop",
    "browser": "Chrome 120",
    "os": "Windows 10",
    "login_at": "2024-01-01T10:30:00Z"
  },
  // ... autres tentatives
]
```

### 23. Statistiques de Connexion
```http
GET /api/auth/login-statistics/?days=30
Authorization: Bearer {access_token}

RÉPONSE 200 OK:
{
  "total_attempts": 45,
  "successful_logins": 42,
  "failed_logins": 3,
  "success_rate": 93.33,
  "devices": {
    "Desktop": 30,
    "Mobile": 12,
    "Tablet": 3
  },
  "browsers": {
    "Chrome": 25,
    "Firefox": 15,
    "Safari": 5
  },
  "countries": {
    "France": 40,
    "Belgium": 5
  },
  "period_days": 30
}
```

---

## ❤️ HEALTH CHECK

### 24. Vérifier l'État du Service
```http
GET /api/auth/health/

RÉPONSE 200 OK:
{
  "status": "healthy",
  "service": "auth-service",
  "version": "1.0.0"
}
```

---

## 🔒 AUTHENTIFICATION

**Tous les endpoints marqués avec `Authorization: Bearer {access_token}` nécessitent un token.**

**Format du header:**
```
Authorization: Bearer votre-access-token-ici
```

---

## ⚠️ CODES D'ERREUR COMMUNS

| Code | Signification | Exemple |
|------|---------------|---------|
| 400 | Bad Request | Données invalides |
| 401 | Unauthorized | Token manquant/invalide |
| 403 | Forbidden | Compte suspendu, email non vérifié |
| 409 | Conflict | Email déjà utilisé |
| 423 | Locked | Compte verrouillé (trop de tentatives) |
| 428 | Precondition Required | MFA requis |
| 500 | Internal Server Error | Erreur serveur |

---

## 🎨 EXEMPLE D'INTÉGRATION FRONTEND (React)

### Configuration Axios
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8001/api/auth',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Intercepteur pour gérer le refresh token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const { data } = await axios.post(
          'http://localhost:8001/api/auth/refresh/',
          { refresh_token: refreshToken }
        );

        localStorage.setItem('access_token', data.session_token);
        localStorage.setItem('refresh_token', data.refresh_token);

        originalRequest.headers.Authorization = `Bearer ${data.session_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Rediriger vers login
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

### Exemple d'Utilisation
```javascript
// Login
const login = async (email, password) => {
  try {
    const { data } = await api.post('/login/', { email, password });
    
    if (data.requires_mfa) {
      // Rediriger vers page MFA
      return { requiresMFA: true, userId: data.user_id };
    }

    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    
    return { user: data.user };
  } catch (error) {
    throw error.response?.data || error;
  }
};

// Register
const register = async (email, username, password) => {
  try {
    const { data } = await api.post('/register/', {
      email,
      username,
      password,
      password_confirm: password,
      role: 'STUDENT'
    });
    return data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

// Get current user
const getCurrentUser = async () => {
  try {
    const { data } = await api.get('/me/');
    return data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

// Logout
const logout = async () => {
  try {
    await api.post('/logout/');
  } finally {
    localStorage.clear();
    window.location.href = '/login';
  }
};
```

---

## 📝 NOTES IMPORTANTES

1. **Tous les tokens expirent** - Utilisez le refresh token pour renouveler
2. **Les sessions durent 24h** par défaut
3. **Les refresh tokens durent 30 jours** par défaut
4. **Compte verrouillé 30 min** après 5 tentatives échouées
5. **MFA codes** - 6 chiffres, 30 secondes de validité
6. **Backup codes** - Usage unique, régénérer après utilisation

---

## 🆘 SUPPORT

Pour toute question, contactez l'équipe backend ou consultez le README.md