from django.db import models

# Areas model ppal
from django.db import models

class Area(models.Model):

    def tiene_dependencias(self):
        """Verifica si el área tiene registros relacionados"""
        from notificaciones.notificadores.models import Notificador
        return Notificador.objects.filter(area=self).exists()

    def tiene_notificadores(self):
        """Verifica si el área tiene notificadores asociados"""
        from notificaciones.notificadores.models import Notificador
        return Notificador.objects.filter(area=self).exists()
        
        
        # # Verificar notificadores asociados
        # if Notificador.objects.filter(area=self).exists():
        #     return True
        # # Verificar bitácoras asociadas (a través de notificador)
        # if Bitacora.objects.filter(notificador__area=self).exists():
        #     return True
        # return False

    # Django creates 'id' as an auto-incrementing integer Primary Key by default
    nombre = models.CharField(max_length=200, unique=True)
    nombre_corto = models.CharField(max_length=50, db_column='NombreCorto')
    extension_telefono = models.CharField(max_length=20, db_column='ExtensionTelefono', blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cat_areas'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre_corto} — {self.nombre}"
