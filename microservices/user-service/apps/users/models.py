"""
Django models sont utilisés uniquement pour l'authentification.
Les données métier sont gérées par Prisma.
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Manager personnalisé pour le modèle User"""
    
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'email est obligatoire')
        if not username:
            raise ValueError('Le username est obligatoire')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Modèle Django pour l'authentification uniquement"""
    
    id = models.UUIDField(primary_key=True, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    username = models.CharField(unique=True, max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'auth_users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
