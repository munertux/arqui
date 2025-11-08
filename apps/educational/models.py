from django.db import models
from apps.core.models import BaseModel
from apps.accounts.models import User

class Category(BaseModel):
    """Categorías para recursos educativos"""
    name = models.CharField(max_length=100, verbose_name='Nombre')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    description = models.TextField(blank=True, verbose_name='Descripción')
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        
    def __str__(self):
        return self.name


class EducationalResource(BaseModel):
    """Modelo para recursos educativos"""
    
    RESOURCE_TYPES = [
        ('article', 'Artículo'),
        ('guide', 'Guía'),
        ('video', 'Video'),
        ('infographic', 'Infografía'),
        ('course', 'Curso'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Título')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Categoría')
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, verbose_name='Tipo')
    content = models.TextField(verbose_name='Contenido')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Autor')
    featured_image = models.ImageField(
        upload_to='educational/', 
        blank=True, 
        null=True, 
        verbose_name='Imagen destacada'
    )
    is_featured = models.BooleanField(default=False, verbose_name='Destacado')
    views_count = models.IntegerField(default=0, verbose_name='Número de vistas')
    
    class Meta:
        verbose_name = 'Recurso educativo'
        verbose_name_plural = 'Recursos educativos'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
