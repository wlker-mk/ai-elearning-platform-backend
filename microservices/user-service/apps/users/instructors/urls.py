from django.urls import path
from .views import (
    InstructorView,
    InstructorVerificationView,
    PublicInstructorView,
    TopInstructorsView,
    InstructorSearchView
)

app_name = 'instructors'

urlpatterns = [
    path('me/', InstructorView.as_view(), name='instructor-me'),
    path('verify/<str:user_id>/', InstructorVerificationView.as_view(), name='instructor-verify'),
    path('top/', TopInstructorsView.as_view(), name='top-instructors'),
    path('search/', InstructorSearchView.as_view(), name='search-instructors'),
    path('<str:user_id>/', PublicInstructorView.as_view(), name='instructor-public'),
]