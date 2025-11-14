from rest_framework import serializers


class StudentSerializer(serializers.Serializer):
    """Serializer pour les étudiants"""
    
    id = serializers.UUIDField(read_only=True)
    user_id = serializers.UUIDField(source='userId', read_only=True)
    student_code = serializers.CharField(source='studentCode', read_only=True)
    points = serializers.IntegerField(read_only=True)
    level = serializers.IntegerField(read_only=True)
    experience_points = serializers.IntegerField(source='experiencePoints', read_only=True)
    streak = serializers.IntegerField(read_only=True)
    max_streak = serializers.IntegerField(source='maxStreak', read_only=True)
    last_activity_date = serializers.DateTimeField(source='lastActivityDate', read_only=True, allow_null=True)
    total_courses_enrolled = serializers.IntegerField(source='totalCoursesEnrolled', read_only=True)
    total_courses_completed = serializers.IntegerField(source='totalCoursesCompleted', read_only=True)
    total_learning_time = serializers.IntegerField(source='totalLearningTime', read_only=True)
    total_certificates = serializers.IntegerField(source='totalCertificates', read_only=True)
    preferred_categories = serializers.ListField(source='preferredCategories', child=serializers.CharField())
    created_at = serializers.DateTimeField(source='createdAt', read_only=True)
    updated_at = serializers.DateTimeField(source='updatedAt', read_only=True)


class StudentCreateSerializer(serializers.Serializer):
    """Serializer pour la création d'un profil étudiant"""
    
    preferred_categories = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )


class StudentUpdateSerializer(serializers.Serializer):
    """Serializer pour la mise à jour d'un profil étudiant"""
    
    preferred_categories = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class AddExperienceSerializer(serializers.Serializer):
    """Serializer pour ajouter de l'expérience"""
    
    points = serializers.IntegerField(min_value=1)