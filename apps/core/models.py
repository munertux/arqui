from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """Modelo base con campos comunes para todas las entidades"""
    created_at = models.DateTimeField(
        default=timezone.now, 
        verbose_name='Fecha de creación',
        help_text='Fecha y hora en que se creó el registro'
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name='Fecha de actualización',
        help_text='Fecha y hora de la última actualización'
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name='Activo',
        help_text='Indica si el registro está activo'
    )
    
    class Meta:
        abstract = True
        
    def __str__(self):
        return f"{self.__class__.__name__} #{self.pk}"

    class Meta:
        abstract = True
