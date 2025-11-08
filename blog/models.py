from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.urls import reverse

from apps.core.models import BaseModel


class BlogCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    slug = models.SlugField(max_length=120, unique=True, verbose_name='Slug')
    description = models.TextField(blank=True, verbose_name='Descripción')

    class Meta:
        verbose_name = 'Categoría del blog'
        verbose_name_plural = 'Categorías del blog'
        ordering = ['name']

    def __str__(self):
        return self.name


class BlogPost(BaseModel):
    category = models.ForeignKey(BlogCategory, on_delete=models.PROTECT, related_name='posts', verbose_name='Categoría')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='blog_posts', verbose_name='Autor')
    title = models.CharField(max_length=200, verbose_name='Título')
    slug = models.SlugField(max_length=220, unique=True, verbose_name='Slug')
    content = models.TextField(verbose_name='Contenido del caso', default='')

    class Meta:
        verbose_name = 'Publicación del blog'
        verbose_name_plural = 'Publicaciones del blog'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})


class BlogImage(BaseModel):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='images', verbose_name='Publicación')
    image = models.ImageField(upload_to='blog/', verbose_name='Imagen')
    caption = models.CharField(max_length=200, blank=True, verbose_name='Descripción de la imagen')

    class Meta:
        verbose_name = 'Imagen de publicación'
        verbose_name_plural = 'Imágenes de publicaciones'
        ordering = ['id']

    def __str__(self):
        return f"Imagen de {self.post.title}"


class BlogComment(BaseModel):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments', verbose_name='Publicación')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='blog_comments', verbose_name='Autor')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', verbose_name='Comentario padre')
    name = models.CharField(max_length=120, blank=True, verbose_name='Nombre')
    email = models.EmailField(blank=True, verbose_name='Correo electrónico')
    content = models.TextField(verbose_name='Comentario')

    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['created_at']

    def __str__(self):
        return f"Comentario en {self.post.title}"

    @property
    def display_name(self):
        if self.author:
            return self.author.get_full_name() or self.author.email
        return self.name or 'Anónimo'

    def active_replies(self):
        cache = getattr(self, '_prefetched_objects_cache', {})
        if 'replies' in cache:
            return [reply for reply in cache['replies'] if reply.is_active]
        return list(self.replies.filter(is_active=True).select_related('author'))


class BlogReaction(BaseModel):
    REACTION_TYPES = [
        ('like', 'Me gusta'),
    ]

    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='reactions', verbose_name='Publicación')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_reactions', verbose_name='Usuario')
    reaction_type = models.CharField(max_length=20, choices=REACTION_TYPES, default='like', verbose_name='Tipo de reacción')

    class Meta:
        verbose_name = 'Reacción'
        verbose_name_plural = 'Reacciones'
        unique_together = ('post', 'user', 'reaction_type')

    def __str__(self):
        return f"{self.user} -> {self.reaction_type} a {self.post}"


class BlogReport(BaseModel):
    TARGET_TYPES = [
        ('post', 'Publicación'),
        ('comment', 'Comentario'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_review', 'En revisión'),
        ('resolved', 'Resuelto'),
        ('dismissed', 'Descartado'),
    ]

    target_type = models.CharField(max_length=20, choices=TARGET_TYPES, verbose_name='Tipo de objetivo')
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='reports', verbose_name='Publicación')
    comment = models.ForeignKey(BlogComment, null=True, blank=True, on_delete=models.CASCADE, related_name='reports', verbose_name='Comentario')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='blog_reports', verbose_name='Reportado por')
    reason = models.TextField(verbose_name='Motivo del reporte')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Estado')
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='blog_reports_processed', verbose_name='Procesado por')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de procesamiento')

    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-created_at']

    def __str__(self):
        target = self.comment or self.post
        return f"Reporte sobre {target}"
