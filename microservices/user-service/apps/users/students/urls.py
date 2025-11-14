from django.urls import path
from .views import (
    StudentView,
    StudentExperienceView,
    StudentStreakView,
    LeaderboardView
)

app_name = 'students'

urlpatterns = [
    path('me/', StudentView.as_view(), name='student-me'),
    path('experience/', StudentExperienceView.as_view(), name='student-experience'),
    path('streak/', StudentStreakView.as_view(), name='student-streak'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
]