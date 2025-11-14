from .course_view_views import TrackCourseViewView, CourseViewStatsView
from .video_analytics_views import (
    VideoAnalyticsView,
    UpdateWatchTimeView,
    UpdateCompletionView,
    VideoEventView,
    LessonEngagementView
)
from .search_log_views import (
    LogSearchView,
    PopularSearchesView,
    ZeroResultSearchesView,
    SearchTrendsView
)
from .user_activity_views import (
    TrackUserActivityView,
    UserActivityHistoryView,
    UserActivityStatsView
)
from .revenue_views import (
    RevenueReportView,
    DailyRevenueView,
    MonthlyRevenueSummaryView
)
from .course_analytics_views import (
    CourseAnalyticsView,
    CourseStatsView,
    TopCoursesView
)

__all__ = [
    'TrackCourseViewView',
    'CourseViewStatsView',
    'VideoAnalyticsView',
    'UpdateWatchTimeView',
    'UpdateCompletionView',
    'VideoEventView',
    'LessonEngagementView',
    'LogSearchView',
    'PopularSearchesView',
    'ZeroResultSearchesView',
    'SearchTrendsView',
    'TrackUserActivityView',
    'UserActivityHistoryView',
    'UserActivityStatsView',
    'RevenueReportView',
    'DailyRevenueView',
    'MonthlyRevenueSummaryView',
    'CourseAnalyticsView',
    'CourseStatsView',
    'TopCoursesView',
]
