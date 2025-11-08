from django.db import models
from apps.core.models import BaseModel
from apps.accounts.models import User

class NewsCategory(BaseModel):
    """Categorías para noticias"""
    name = models.CharField(max_length=100, verbose_name='Nombre')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    description = models.TextField(blank=True, verbose_name='Descripción')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Color')
    
    class Meta:
        verbose_name = 'Categoría de noticias'
        verbose_name_plural = 'Categorías de noticias'
        
    def __str__(self):
        return self.name


class NewsPost(BaseModel):
    """Modelo para publicaciones de noticias"""
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
        ('archived', 'Archivado'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Título')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE, verbose_name='Categoría')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Autor')
    excerpt = models.TextField(max_length=300, verbose_name='Resumen')
    content = models.TextField(verbose_name='Contenido')
    featured_image = models.ImageField(
        upload_to='news/', 
        blank=True, 
        null=True, 
        verbose_name='Imagen destacada'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Estado')
    is_featured = models.BooleanField(default=False, verbose_name='Destacado')
    published_at = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de publicación')
    views_count = models.IntegerField(default=0, verbose_name='Número de vistas')
    tags = models.CharField(max_length=500, blank=True, verbose_name='Etiquetas (separadas por comas)')
    
    class Meta:
        verbose_name = 'Noticia'
        verbose_name_plural = 'Noticias'
        ordering = ['-published_at', '-created_at']
        
    def __str__(self):
        return self.title
