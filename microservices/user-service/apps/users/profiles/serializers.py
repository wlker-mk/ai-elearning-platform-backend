from rest_framework import serializers
from datetime import datetime


class ProfileSerializer(serializers.Serializer):
    """Serializer pour les profils utilisateurs"""
    
    id = serializers.UUIDField(read_only=True)
    user_id = serializers.UUIDField(source='userId')
    first_name = serializers.CharField(source='firstName', max_length=100)
    last_name = serializers.CharField(source='lastName', max_length=100)
    phone_number = serializers.CharField(source='phoneNumber', required=False, allow_null=True)
    date_of_birth = serializers.DateField(source='dateOfBirth', required=False, allow_null=True)
    profile_image_url = serializers.URLField(source='profileImageUrl', required=False, allow_null=True)
    cover_image_url = serializers.URLField(source='coverImageUrl', required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    website = serializers.URLField(required=False, allow_null=True)
    linkedin = serializers.URLField(required=False, allow_null=True)
    github = serializers.URLField(required=False, allow_null=True)
    twitter = serializers.URLField(required=False, allow_null=True)
    facebook = serializers.URLField(required=False, allow_null=True)
    country = serializers.CharField(required=False, allow_null=True)
    city = serializers.CharField(required=False, allow_null=True)
    timezone = serializers.CharField(default='UTC')
    language = serializers.CharField(default='en')
    created_at = serializers.DateTimeField(source='createdAt', read_only=True)
    updated_at = serializers.DateTimeField(source='updatedAt', read_only=True)


class ProfileCreateSerializer(serializers.Serializer):
    """Serializer pour la création de profil"""
    
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(required=False, allow_null=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    profile_image_url = serializers.URLField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    country = serializers.CharField(required=False, allow_null=True)
    city = serializers.CharField(required=False, allow_null=True)
    timezone = serializers.CharField(default='UTC')
    language = serializers.CharField(default='en')


class ProfileUpdateSerializer(serializers.Serializer):
    """Serializer pour la mise à jour de profil"""
    
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    phone_number = serializers.CharField(required=False, allow_null=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    # CORRECTION : Ajouter required=False
    profile_image_url = serializers.URLField(required=False, allow_null=True)
    cover_image_url = serializers.URLField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    website = serializers.URLField(required=False, allow_null=True)
    linkedin = serializers.URLField(required=False, allow_null=True)
    github = serializers.URLField(required=False, allow_null=True)
    twitter = serializers.URLField(required=False, allow_null=True)
    facebook = serializers.URLField(required=False, allow_null=True)
    country = serializers.CharField(required=False, allow_null=True)
    city = serializers.CharField(required=False, allow_null=True)
    timezone = serializers.CharField(required=False)
    language = serializers.CharField(required=False)
