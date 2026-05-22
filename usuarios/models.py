from django.db import models
from django.contrib.auth.models import AbstractUser

from django.db import models
from django.contrib.auth.models import AbstractUser

class UsuarioPerfil(AbstractUser):
    ROLES_CHOICES = [
        ('coordinador', 'Coordinador'),
        ('secretaria', 'Secretaría'),
        ('notificador', 'Notificador'),
        ('admin', 'Administrador de Área'),
        ('developer', 'Developer Global'),
    ]

    rol = models.CharField(max_length=20, choices=ROLES_CHOICES, default='notificador')
    
    
    area = models.ForeignKey(
        'areas.Area', 
        on_delete=models.PROTECT, 
        related_name='usuarios_perfiles', 
        null=True, 
        blank=True
    )

    # --- SOLUCIÓN AL ERROR E304: Forzar nombres inversos únicos ---
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuarios_perfiles_groups', # Nombre único
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuarios_perfiles_permissions', # Nombre único
        blank=True,
        help_text='Specific permissions for this user.'
    )

    class Meta:
        db_table = 'auth_usuarios_perfiles'

    def __str__(self):
        area_nombre = self.area.nombre if self.area else "Global"
        return f"{self.username} ({self.get_rol_display()}) — {area_nombre}"


