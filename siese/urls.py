"""
SIESE - Sistema Integral de Energía Solar en Colombia
Configuración principal de URLs
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Panel de administración
    path('admin/', admin.site.urls),
    
    # URLs de las aplicaciones
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('simulator/', include('apps.simulator.urls')),
    path('monitoring/', include('apps.monitoring.urls')),
    path('education/', include('apps.educational.urls')),
    path('regulatory/', include('apps.regulatory.urls')),
    path('news/', include('apps.news.urls')),
    path('blog/', include('blog.urls')),
    
    # API URLs
    path('api/v1/', include('apps.core.api_urls')),
]

# Configuración para archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Configuración del panel de administración
admin.site.site_header = "SIESE - Administración"
admin.site.site_title = "SIESE Admin"
admin.site.index_title = "Panel de Administración"
