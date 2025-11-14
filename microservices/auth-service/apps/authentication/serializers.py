from rest_framework import serializers
from datetime import datetime


# ============ Auth Serializers ============

class RegisterSerializer(serializers.Serializer):
    """Serializer pour l'inscription"""
    email = serializers.EmailField()
    username = serializers.CharField(min_length=3, max_length=50)
    password = serializers.CharField(min_length=8, write_only=True)
    password_confirm = serializers.CharField(min_length=8, write_only=True)
    role = serializers.ChoiceField(
        choices=['STUDENT', 'INSTRUCTOR'],
        default='STUDENT'
    )
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data


class LoginSerializer(serializers.Serializer):
    """Serializer pour la connexion"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    remember_me = serializers.BooleanField(default=False, required=False)


class MFALoginSerializer(serializers.Serializer):
    """Serializer pour la connexion avec MFA"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    mfa_code = serializers.CharField(min_length=6, max_length=8)


class VerifyEmailSerializer(serializers.Serializer):
    """Serializer pour la vérification d'email"""
    token = serializers.CharField()


class RequestPasswordResetSerializer(serializers.Serializer):
    """Serializer pour demander une réinitialisation de mot de passe"""
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer pour réinitialiser le mot de passe"""
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)
    new_password_confirm = serializers.CharField(min_length=8, write_only=True)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour changer le mot de passe"""
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)
    new_password_confirm = serializers.CharField(min_length=8, write_only=True)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        if data['current_password'] == data['new_password']:
            raise serializers.ValidationError("New password must be different from current password")
        return data


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer pour rafraîchir le token"""
    refresh_token = serializers.CharField()


# ============ MFA Serializers ============

class EnableMFASerializer(serializers.Serializer):
    """Serializer pour activer le MFA"""
    pass


class VerifyMFASerializer(serializers.Serializer):
    """Serializer pour vérifier et activer le MFA"""
    code = serializers.CharField(min_length=6, max_length=6)


class DisableMFASerializer(serializers.Serializer):
    """Serializer pour désactiver le MFA"""
    password = serializers.CharField(write_only=True)


class VerifyMFACodeSerializer(serializers.Serializer):
    """Serializer pour vérifier un code MFA"""
    code = serializers.CharField(min_length=6, max_length=8)


# ============ User Serializers ============

class UserSerializer(serializers.Serializer):
    """Serializer pour les utilisateurs"""
    id = serializers.UUIDField(read_only=True)
    username = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.CharField()
    is_email_verified = serializers.BooleanField(source='isEmailVerified', read_only=True)
    is_active = serializers.BooleanField(source='isActive', read_only=True)
    is_suspended = serializers.BooleanField(source='isSuspended', read_only=True)
    mfa_enabled = serializers.BooleanField(source='mfaEnabled', read_only=True)
    last_login_at = serializers.DateTimeField(source='lastLoginAt', read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(source='createdAt', read_only=True)


class SessionSerializer(serializers.Serializer):
    """Serializer pour les sessions"""
    id = serializers.UUIDField(read_only=True)
    token = serializers.CharField(read_only=True)
    expires_at = serializers.DateTimeField(source='expiresAt', read_only=True)
    ip_address = serializers.IPAddressField(source='ipAddress', read_only=True, allow_null=True)
    device = serializers.CharField(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(source='createdAt', read_only=True)


class LoginHistorySerializer(serializers.Serializer):
    """Serializer pour l'historique de connexion"""
    id = serializers.UUIDField(read_only=True)
    success = serializers.BooleanField()
    failure_reason = serializers.CharField(source='failureReason', allow_null=True)
    ip_address = serializers.IPAddressField(source='ipAddress', allow_null=True)
    location = serializers.CharField(allow_null=True)
    country = serializers.CharField(allow_null=True)
    city = serializers.CharField(allow_null=True)
    device = serializers.CharField(allow_null=True)
    browser = serializers.CharField(allow_null=True)
    os = serializers.CharField(allow_null=True)
    login_at = serializers.DateTimeField(source='loginAt', read_only=True)
