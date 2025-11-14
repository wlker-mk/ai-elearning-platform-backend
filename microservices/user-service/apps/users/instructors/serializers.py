from rest_framework import serializers


class InstructorSerializer(serializers.Serializer):
    """Serializer pour les instructeurs"""
    
    id = serializers.UUIDField(read_only=True)
    user_id = serializers.UUIDField(source='userId', read_only=True)
    instructor_code = serializers.CharField(source='instructorCode', read_only=True)
    title = serializers.CharField(required=False, allow_null=True)
    headline = serializers.CharField(required=False, allow_null=True)
    specializations = serializers.ListField(child=serializers.CharField())
    expertise = serializers.ListField(child=serializers.CharField())
    certifications = serializers.ListField(child=serializers.CharField())
    years_of_experience = serializers.IntegerField(source='yearsOfExperience')
    hourly_rate = serializers.FloatField(source='hourlyRate', required=False, allow_null=True)
    rating = serializers.FloatField(read_only=True)
    total_reviews = serializers.IntegerField(source='totalReviews', read_only=True)
    total_students = serializers.IntegerField(source='totalStudents', read_only=True)
    total_courses = serializers.IntegerField(source='totalCourses', read_only=True)
    is_verified = serializers.BooleanField(source='isVerified', read_only=True)
    verified_at = serializers.DateTimeField(source='verifiedAt', read_only=True, allow_null=True)
    bank_account = serializers.CharField(source='bankAccount', required=False, allow_null=True, write_only=True)
    bank_name = serializers.CharField(source='bankName', required=False, allow_null=True, write_only=True)
    paypal_email = serializers.EmailField(source='paypalEmail', required=False, allow_null=True, write_only=True)
    created_at = serializers.DateTimeField(source='createdAt', read_only=True)
    updated_at = serializers.DateTimeField(source='updatedAt', read_only=True)


class InstructorCreateSerializer(serializers.Serializer):
    """Serializer pour la création d'un profil instructeur"""
    
    title = serializers.CharField(required=False, allow_null=True, max_length=100)
    headline = serializers.CharField(required=False, allow_null=True, max_length=255)
    specializations = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    expertise = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    certifications = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    years_of_experience = serializers.IntegerField(default=0, min_value=0)
    hourly_rate = serializers.FloatField(required=False, allow_null=True, min_value=0)
    bank_account = serializers.CharField(required=False, allow_null=True)
    bank_name = serializers.CharField(required=False, allow_null=True)
    paypal_email = serializers.EmailField(required=False, allow_null=True)


class InstructorUpdateSerializer(serializers.Serializer):
    """Serializer pour la mise à jour d'un profil instructeur"""
    
    title = serializers.CharField(required=False, max_length=100)
    headline = serializers.CharField(required=False, max_length=255)
    specializations = serializers.ListField(child=serializers.CharField(), required=False)
    expertise = serializers.ListField(child=serializers.CharField(), required=False)
    certifications = serializers.ListField(child=serializers.CharField(), required=False)
    years_of_experience = serializers.IntegerField(required=False, min_value=0)
    hourly_rate = serializers.FloatField(required=False, min_value=0)
    bank_account = serializers.CharField(required=False)
    bank_name = serializers.CharField(required=False)
    paypal_email = serializers.EmailField(required=False)


class InstructorPublicSerializer(serializers.Serializer):
    """Serializer pour les profils publics (sans infos bancaires)"""
    
    id = serializers.UUIDField(read_only=True)
    user_id = serializers.UUIDField(source='userId', read_only=True)
    instructor_code = serializers.CharField(source='instructorCode', read_only=True)
    title = serializers.CharField()
    headline = serializers.CharField()
    specializations = serializers.ListField(child=serializers.CharField())
    expertise = serializers.ListField(child=serializers.CharField())
    certifications = serializers.ListField(child=serializers.CharField())
    years_of_experience = serializers.IntegerField(source='yearsOfExperience')
    hourly_rate = serializers.FloatField(source='hourlyRate')
    rating = serializers.FloatField()
    total_reviews = serializers.IntegerField(source='totalReviews')
    total_students = serializers.IntegerField(source='totalStudents')
    total_courses = serializers.IntegerField(source='totalCourses')
    is_verified = serializers.BooleanField(source='isVerified')


class RatingSerializer(serializers.Serializer):
    """Serializer pour ajouter une note"""
    
    rating = serializers.FloatField(min_value=0.0, max_value=5.0)
