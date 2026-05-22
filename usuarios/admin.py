from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioPerfil

@admin.register(UsuarioPerfil)
class UsuarioPerfilAdmin(UserAdmin):
    # Columnas visibles en la lista de usuarios
    list_display = ('username', 'email', 'rol', 'area', 'is_staff', 'is_active')
    # Filtros laterales rápidos
    list_filter = ('rol', 'area', 'is_staff', 'is_active')
    # Buscador de usuarios
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    # Estructura de los formularios de edición en el Admin
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Control V2 (XTIANE)', {
            'fields': ('rol', 'area'),
        }),
    )
    # Estructura del formulario de creación de nuevos usuarios
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Control V2 (XTIANE)', {
            'fields': ('rol', 'area'),
        }),
    )
