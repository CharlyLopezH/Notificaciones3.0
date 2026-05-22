from django.contrib import admin
from .models import Area

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'nombre_corto', 'extension_telefono', 'fecha_registro')
    search_fields = ('nombre', 'nombre_corto', 'extension_telefono')
    ordering = ('nombre',)
