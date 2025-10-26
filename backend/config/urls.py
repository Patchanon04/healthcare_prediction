"""
URL configuration for the backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('predictions.urls')),
]

# Serve media files so that internal services (e.g., ML service) can fetch uploaded images
# Note: In production, it's recommended to serve media via a dedicated web server like Nginx.
# We enable this here to allow the ML service (inside Docker network) to access files at
# http://medml_backend:8000/media/...
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
