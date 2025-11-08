from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('simulator/', include('apps.simulator.api_urls')),
    path('monitoring/', include('apps.monitoring.api_urls')),
    path('educational/', include('apps.educational.api_urls')),
    path('regulatory/', include('apps.regulatory.api_urls')),
    path('news/', include('apps.news.api_urls')),
]
