from django.db import models
from django.urls import reverse
from apps.core.models import BaseModel
import bleach

class LegalFramework(BaseModel):
    """Modelo para almacenar marcos legales y normativas"""
    
    DOCUMENT_TYPES = [
        ('ley', 'Ley'),
        ('decreto', 'Decreto'),
        ('resolucion', 'Resolución'),
        ('circular', 'Circular'),
        ('guia', 'Guía'),
    ]
    
    title = models.CharField(
        max_length=300,
        verbose_name='Título',
        help_text='Título completo del documento legal'
    )
    
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        default='ley',
        verbose_name='Tipo de documento'
    )
    
    document_number = models.CharField(
        max_length=50,
        verbose_name='Número de documento',
        help_text='Ej: 1715, 2492, etc.'
    )
    
    year = models.PositiveIntegerField(
        verbose_name='Año',
        help_text='Año de expedición',
        db_index=True
    )

    issuing_entity = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Entidad emisora',
        help_text='Ministerio, agencia u organismo que expide la normativa',
        db_index=True
    )
    
    summary = models.TextField(
        verbose_name='Resumen',
        help_text='Resumen en lenguaje claro y comprensible'
    )
    
    main_objective = models.TextField(
        verbose_name='Objetivo principal',
        help_text='Objetivo principal de la norma'
    )
    
    benefits_companies = models.TextField(
        verbose_name='Beneficios para empresas',
        blank=True,
        help_text='Beneficios específicos para empresas'
    )
    
    benefits_citizens = models.TextField(
        verbose_name='Beneficios para ciudadanos',
        blank=True,
        help_text='Beneficios específicos para ciudadanos'
    )
    
    official_url = models.URLField(
        verbose_name='URL oficial',
        help_text='Enlace a la fuente oficial'
    )
    
    content_scraped = models.TextField(
        verbose_name='Contenido scrapeado',
        blank=True,
        help_text='Contenido obtenido mediante scraping'
    )
    
    last_scraped = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última actualización de scraping'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Si está activo para mostrar en el sitio'
    )
    
    class Meta:
        verbose_name = 'Marco Legal'
        verbose_name_plural = 'Marcos Legales'
        ordering = ['-year', 'document_number']
    
    def __str__(self):
        return f"{self.get_document_type_display()} {self.document_number} de {self.year}"
    
    def get_absolute_url(self):
        return reverse('regulatory:detail', kwargs={'pk': self.pk})
    
    def clean_content(self, content):
        """Limpia y sanitiza el contenido scrapeado, preservando formato básico"""
        allowed_tags = [
            'p', 'br', 'strong', 'b', 'em', 'i', 'u',
            'ul', 'ol', 'li', 'blockquote',
            'h1', 'h2', 'h3', 'h4',
            'a',
            'table', 'thead', 'tbody', 'tr', 'td', 'th'
        ]
        allowed_attrs = {
            'a': ['href', 'title', 'target', 'rel'],
            'td': ['colspan', 'rowspan'],
            'th': ['colspan', 'rowspan']
        }
        allowed_protocols = ['http', 'https', 'mailto']
        # Nota: no se permiten estilos inline por seguridad
        return bleach.clean(
            content or '',
            tags=allowed_tags,
            attributes=allowed_attrs,
            protocols=allowed_protocols,
            strip=True
        )


class ScrapingSource(BaseModel):
    """Fuentes para realizar scraping de información legal"""
    
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre de la fuente'
    )
    
    base_url = models.URLField(
        verbose_name='URL base'
    )
    
    selector_title = models.CharField(
        max_length=200,
        verbose_name='Selector CSS para título',
        blank=True
    )
    
    selector_content = models.CharField(
        max_length=200,
        verbose_name='Selector CSS para contenido',
        blank=True
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        verbose_name = 'Fuente de Scraping'
        verbose_name_plural = 'Fuentes de Scraping'
    
    def __str__(self):
        return self.name


class RegulatoryCategory(BaseModel):
    """Categorías para normativas"""
    name = models.CharField(max_length=100, verbose_name='Nombre')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    description = models.TextField(blank=True, verbose_name='Descripción')
    
    class Meta:
        verbose_name = 'Categoría regulatoria'
        verbose_name_plural = 'Categorías regulatorias'
        
    def __str__(self):
        return self.name


class RegulatoryDocument(BaseModel):
    """Modelo para documentos regulatorios"""
    
    DOCUMENT_TYPES = [
        ('law', 'Ley'),
        ('decree', 'Decreto'),
        ('resolution', 'Resolución'),
        ('circular', 'Circular'),
        ('standard', 'Norma técnica'),
        ('guideline', 'Lineamiento'),
    ]
    
    title = models.CharField(max_length=300, verbose_name='Título')
    document_number = models.CharField(max_length=50, verbose_name='Número de documento')
    category = models.ForeignKey(
        RegulatoryCategory, 
        on_delete=models.CASCADE, 
        verbose_name='Categoría'
    )
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, verbose_name='Tipo')
    issuing_entity = models.CharField(max_length=200, verbose_name='Entidad emisora')
    publication_date = models.DateField(verbose_name='Fecha de publicación')
    effective_date = models.DateField(verbose_name='Fecha de vigencia')
    summary = models.TextField(verbose_name='Resumen')
    full_text = models.TextField(blank=True, verbose_name='Texto completo')
    document_file = models.FileField(
        upload_to='regulatory/', 
        blank=True, 
        null=True, 
        verbose_name='Archivo del documento'
    )
    external_url = models.URLField(blank=True, verbose_name='URL externa')
    tags = models.CharField(max_length=500, blank=True, verbose_name='Etiquetas (separadas por comas)')
    
    class Meta:
        verbose_name = 'Documento regulatorio'
        verbose_name_plural = 'Documentos regulatorios'
        ordering = ['-publication_date']
        
    def __str__(self):
        return f"{self.document_number} - {self.title}"
