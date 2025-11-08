from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class EducationalHomeView(TemplateView):
    """Vista principal de recursos educativos"""
    template_name = 'educational/home.html'

class CategoryView(TemplateView):
    """Vista de categoría de recursos"""
    template_name = 'educational/category.html'

class ResourceDetailView(TemplateView):
    """Vista de detalle del recurso"""
    template_name = 'educational/resource_detail.html'
