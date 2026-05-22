from django.contrib import admin
from .models import Notificador

@admin.register(Notificador)
class NotificadorAdmin(admin.ModelAdmin):
    list_display = ('id', 'apellido1', 'apellido2', 'nombres', 'area', 'telefono_emergencia')
    list_filter = ('area',) # Filtro rápido por área organizativa
    search_fields = ('nombres', 'apellido1', 'apellido2', 'telefono_emergencia')
    ordering = ('apellido1', 'apellido2', 'nombres')
