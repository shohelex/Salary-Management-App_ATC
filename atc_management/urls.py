"""URL configuration for ATC Management System."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('factory/', include('factory.urls')),
    path('depot/', include('depot.urls')),
    path('expenses/', include('expenses.urls')),
    path('finance/', include('finance.urls')),
    path('suppliers/', include('suppliers.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
