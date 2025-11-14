from django.urls import path
from .views import ProfileView, PublicProfileView

app_name = 'profiles'

urlpatterns = [
    path('me/', ProfileView.as_view(), name='profile-me'),
    path('<str:user_id>/', PublicProfileView.as_view(), name='profile-public'),
]