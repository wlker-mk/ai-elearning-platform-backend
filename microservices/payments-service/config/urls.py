from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        "status": "healthy", 
        "service": "payments",
        "version": "1.0.0"
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Payments URLs
    path('api/payments/health/', health_check, name='health_check'),
    path('api/', include('apps.payments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)