from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    """Modelo base abstracto para todos los modelos del proyecto"""
    
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name='Fecha de actualización'
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name='Activo'
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para agregar lógica personalizada"""
        if not self.pk:
            # Es un objeto nuevo
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
