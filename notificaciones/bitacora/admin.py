# notificaciones/bitacora/admin.py
from django.contrib import admin
from .models import Bitacora

@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'oficio_memo',
        'destinatario',
        'situacion',  # ← Cambiado: antes era 'area'
        'notificador',
        'fecha_termino',
        'fecha_acuse',
        'fecha_registro',
    ]
    
    list_filter = [
        'situacion',  # ← Cambiado: antes era 'area'
        'notificador',
        'fecha_termino',
        'fecha_acuse',
    ]
    
    search_fields = [
        'oficio_memo',
        'destinatario',
        'expediente_asunto',
        'notificador__nombres',
        'notificador__apellido1',
    ]
    
    readonly_fields = ['fecha_registro']
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('oficio_memo', 'situacion', 'destinatario', 'notificador')
        }),
        ('Fechas', {
            'fields': ('fecha_bitacora', 'fecha_termino', 'fecha_acuse', 'fecha_registro')
        }),
        ('Contenido', {
            'fields': ('expediente_asunto', 'pdf_adjunto')
        }),
        ('Seguimiento', {
            'fields': ('en_ruta', 'fecha_salida_ruta')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('notificador')