from django.urls import path, include

urlpatterns = [
    path('profiles/', include('apps.users.profiles.urls')),
    path('instructors/', include('apps.users.instructors.urls')),
    path('students/', include('apps.users.students.urls')),
]