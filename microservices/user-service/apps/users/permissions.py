# apps/users/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow owners to edit, others to read only"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.userId == str(request.user.id)

class IsInstructor(permissions.BasePermission):
    """Check if user is an instructor"""
    def has_permission(self, request, view):
        # Cette vérification nécessite un champ 'role' dans le User model
        return hasattr(request.user, 'role') and request.user.role == 'instructor'

class IsStudent(permissions.BasePermission):
    """Check if user is a student"""
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'student'