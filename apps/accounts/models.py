from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel


class Role(BaseModel):
    """Rol del sistema que puede asignarse a múltiples usuarios."""

    slug = models.SlugField(unique=True, verbose_name='Identificador')
    name = models.CharField(max_length=50, unique=True, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    is_active = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['name']

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Modelo de usuario personalizado"""
    
    ROLE_CHOICES = [
        ('client', 'Cliente/Usuario'),
        ('editor', 'Editor'),
        ('admin', 'Administrador'),
        ('analyst', 'Analista'),
    ]
    
    email = models.EmailField(unique=True, verbose_name='Correo electrónico')
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='client',
        verbose_name='Rol principal'
    )
    roles = models.ManyToManyField(
        'accounts.Role',
        related_name='users',
        blank=True,
        verbose_name='Roles adicionales'
    )
    phone = models.CharField(max_length=15, blank=True, verbose_name='Teléfono')
    location = models.CharField(max_length=100, blank=True, verbose_name='Ubicación')
    is_email_verified = models.BooleanField(default=False, verbose_name='Email verificado')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        
    def __str__(self):
        return f"{self.email} - {self.get_role_display()}"

    def add_role(self, slug):
        """Asigna un rol adicional al usuario a partir del slug."""
        try:
            role = Role.objects.get(slug=slug, is_active=True)
        except Role.DoesNotExist:
            return
        self.roles.add(role)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_editor(self):
        return self.role == 'editor' or self.has_role('editor')

    @property
    def is_client(self):
        return self.role == 'client' or self.has_role('client')

    def has_role(self, slug):
        """Verifica si el usuario posee un rol específico."""
        return self.role == slug or self.roles.filter(slug=slug, is_active=True).exists()

    @property
    def is_admin_role(self):
        return self.role == 'admin' or self.has_role('admin')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_superuser:
            try:
                admin_role = Role.objects.get(slug='admin', is_active=True)
                self.roles.add(admin_role)
            except Role.DoesNotExist:
                pass


class UserProfile(BaseModel):
    """Perfil extendido del usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, verbose_name='Biografía')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Avatar')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Fecha de nacimiento')
    company = models.CharField(max_length=100, blank=True, verbose_name='Empresa')
    website = models.URLField(blank=True, verbose_name='Sitio web')
    
    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'
        
    def __str__(self):
        return f"Perfil de {self.user.full_name}"


class PasswordResetCode(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_codes')
    code = models.CharField(max_length=6, verbose_name='Código')
    is_used = models.BooleanField(default=False, verbose_name='Usado')
    expires_at = models.DateTimeField(verbose_name='Expira el')

    class Meta:
        verbose_name = 'Código de restablecimiento de contraseña'
        verbose_name_plural = 'Códigos de restablecimiento de contraseña'
        ordering = ['-created_at']

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at
