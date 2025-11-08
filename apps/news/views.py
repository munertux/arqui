from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class NewsHomeView(TemplateView):
    """Vista principal de noticias"""
    template_name = 'news/home.html'

class CategoryView(TemplateView):
    """Vista de categoría de noticias"""
    template_name = 'news/category.html'

class PostDetailView(TemplateView):
    """Vista de detalle de la noticia"""
    template_name = 'news/post_detail.html'

class CreatePostView(TemplateView):
    """Vista para crear una nueva noticia"""
    template_name = 'news/create_post.html'
