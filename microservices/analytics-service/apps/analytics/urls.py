from django.urls import path
from apps.analytics.views import (
    # Course Views
    TrackCourseViewView,
    CourseViewStatsView,
    # Video Analytics
    VideoAnalyticsView,
    UpdateWatchTimeView,
    UpdateCompletionView,
    VideoEventView,
    LessonEngagementView,
    # Search Logs
    LogSearchView,
    PopularSearchesView,
    ZeroResultSearchesView,
    SearchTrendsView,
    # User Activity
    TrackUserActivityView,
    UserActivityHistoryView,
    UserActivityStatsView,
    # Revenue
    RevenueReportView,
    DailyRevenueView,
    MonthlyRevenueSummaryView,
    # Course Analytics
    CourseAnalyticsView,
    CourseStatsView,
    TopCoursesView,
)

app_name = 'analytics'

urlpatterns = [
    # Course Views
    path('course-views/track/', TrackCourseViewView.as_view(), name='track-course-view'),
    path('course-views/stats/<str:course_id>/', CourseViewStatsView.as_view(), name='course-view-stats'),
    
    # Video Analytics
    path('video/analytics/', VideoAnalyticsView.as_view(), name='video-analytics'),
    path('video/watch-time/', UpdateWatchTimeView.as_view(), name='update-watch-time'),
    path('video/completion/', UpdateCompletionView.as_view(), name='update-completion'),
    path('video/event/', VideoEventView.as_view(), name='video-event'),
    path('video/engagement/<str:lesson_id>/', LessonEngagementView.as_view(), name='lesson-engagement'),
    
    # Search Logs
    path('search/log/', LogSearchView.as_view(), name='log-search'),
    path('search/popular/', PopularSearchesView.as_view(), name='popular-searches'),
    path('search/zero-results/', ZeroResultSearchesView.as_view(), name='zero-result-searches'),
    path('search/trends/', SearchTrendsView.as_view(), name='search-trends'),
    
    # User Activity
    path('activity/track/', TrackUserActivityView.as_view(), name='track-activity'),
    path('activity/history/<str:user_id>/', UserActivityHistoryView.as_view(), name='activity-history'),
    path('activity/stats/<str:user_id>/', UserActivityStatsView.as_view(), name='activity-stats'),
    
    # Revenue
    path('revenue/report/', RevenueReportView.as_view(), name='revenue-report'),
    path('revenue/daily/', DailyRevenueView.as_view(), name='daily-revenue'),
    path('revenue/monthly/', MonthlyRevenueSummaryView.as_view(), name='monthly-revenue'),
    
    # Course Analytics
    path('course/analytics/', CourseAnalyticsView.as_view(), name='course-analytics'),
    path('course/stats/<str:course_id>/', CourseStatsView.as_view(), name='course-stats'),
    path('course/top/', TopCoursesView.as_view(), name='top-courses'),
]