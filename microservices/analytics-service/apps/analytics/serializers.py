from rest_framework import serializers
from datetime import date, datetime


# ============ Course Views Serializers ============

class CourseViewSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    course_id = serializers.UUIDField(source='courseId')
    user_id = serializers.UUIDField(source='userId', required=False, allow_null=True)
    ip_address = serializers.IPAddressField(source='ipAddress', required=False, allow_null=True)
    user_agent = serializers.CharField(source='userAgent', required=False, allow_null=True)
    country = serializers.CharField(required=False, allow_null=True)
    city = serializers.CharField(required=False, allow_null=True)
    referrer = serializers.URLField(required=False, allow_null=True)
    source = serializers.CharField(required=False, allow_null=True)
    viewed_at = serializers.DateTimeField(source='viewedAt', read_only=True)


class TrackCourseViewSerializer(serializers.Serializer):
    course_id = serializers.UUIDField()
    user_id = serializers.UUIDField(required=False, allow_null=True)
    country = serializers.CharField(required=False, allow_null=True)
    city = serializers.CharField(required=False, allow_null=True)
    referrer = serializers.URLField(required=False, allow_null=True)
    source = serializers.CharField(required=False, allow_null=True)


# ============ Video Analytics Serializers ============

class VideoAnalyticsSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    lesson_id = serializers.UUIDField(source='lessonId')
    student_id = serializers.UUIDField(source='studentId')
    total_watch_time = serializers.IntegerField(source='totalWatchTime')
    completion_rate = serializers.FloatField(source='completionRate')
    pause_count = serializers.IntegerField(source='pauseCount')
    rewind_count = serializers.IntegerField(source='rewindCount')
    speed_changes = serializers.IntegerField(source='speedChanges')
    avg_quality = serializers.CharField(source='avgQuality', allow_null=True)
    last_position = serializers.IntegerField(source='lastPosition')
    created_at = serializers.DateTimeField(source='createdAt', read_only=True)
    updated_at = serializers.DateTimeField(source='updatedAt', read_only=True)


class UpdateWatchTimeSerializer(serializers.Serializer):
    lesson_id = serializers.UUIDField()
    student_id = serializers.UUIDField()
    watch_time = serializers.IntegerField(min_value=0)
    position = serializers.IntegerField(min_value=0)


class UpdateCompletionSerializer(serializers.Serializer):
    lesson_id = serializers.UUIDField()
    student_id = serializers.UUIDField()
    completion_rate = serializers.FloatField(min_value=0.0, max_value=100.0)


class VideoEventSerializer(serializers.Serializer):
    lesson_id = serializers.UUIDField()
    student_id = serializers.UUIDField()
    event_type = serializers.ChoiceField(choices=['pause', 'rewind', 'speed_change', 'quality'])
    quality = serializers.CharField(required=False, allow_null=True)


# ============ Search Log Serializers ============

class SearchLogSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    query = serializers.CharField()
    user_id = serializers.UUIDField(source='userId', required=False, allow_null=True)
    ip_address = serializers.IPAddressField(source='ipAddress', required=False, allow_null=True)
    results_count = serializers.IntegerField(source='resultsCount')
    clicked_result = serializers.CharField(source='clickedResult', required=False, allow_null=True)
    searched_at = serializers.DateTimeField(source='searchedAt', read_only=True)


class LogSearchSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=255)
    results_count = serializers.IntegerField(min_value=0)
    user_id = serializers.UUIDField(required=False, allow_null=True)
    clicked_result = serializers.CharField(required=False, allow_null=True)


# ============ User Activity Serializers ============

class UserActivitySerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    user_id = serializers.UUIDField(source='userId')
    event_type = serializers.CharField(source='eventType')
    metadata = serializers.JSONField(required=False, allow_null=True)
    created_at = serializers.DateTimeField(source='createdAt', read_only=True)


class TrackActivitySerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    event_type = serializers.CharField(max_length=100)
    metadata = serializers.JSONField(required=False, allow_null=True)


# ============ Revenue Report Serializers ============

class RevenueReportSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    date = serializers.DateField()
    total_revenue = serializers.FloatField(source='totalRevenue')
    total_orders = serializers.IntegerField(source='totalOrders')
    created_at = serializers.DateTimeField(source='createdAt', read_only=True)


class CreateRevenueReportSerializer(serializers.Serializer):
    date = serializers.DateField()
    revenue = serializers.FloatField(min_value=0)
    orders = serializers.IntegerField(min_value=0)


# ============ Course Analytics Serializers ============

class CourseAnalyticsSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    course_id = serializers.UUIDField(source='courseId')
    date = serializers.DateField()
    views = serializers.IntegerField()
    enrollments = serializers.IntegerField()
    completions = serializers.IntegerField()
    avg_rating = serializers.FloatField(source='avgRating', allow_null=True)
    created_at = serializers.DateTimeField(source='createdAt', read_only=True)


class UpdateCourseAnalyticsSerializer(serializers.Serializer):
    course_id = serializers.UUIDField()
    date = serializers.DateField(required=False)
    views = serializers.IntegerField(required=False, min_value=0, default=0)
    enrollments = serializers.IntegerField(required=False, min_value=0, default=0)
    completions = serializers.IntegerField(required=False, min_value=0, default=0)
    rating = serializers.FloatField(required=False, min_value=0.0, max_value=5.0)