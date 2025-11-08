from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('system/<int:system_id>/', views.SystemDetailView.as_view(), name='system_detail'),
    path('reports/', views.ReportsView.as_view(), name='reports'),
]
