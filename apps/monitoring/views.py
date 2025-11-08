from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class DashboardView(TemplateView):
    """Vista del dashboard de monitoreo"""
    template_name = 'monitoring/dashboard.html'

class SystemDetailView(TemplateView):
    """Vista de detalle del sistema"""
    template_name = 'monitoring/system_detail.html'

class ReportsView(TemplateView):
    """Vista de reportes"""
    template_name = 'monitoring/reports.html'
