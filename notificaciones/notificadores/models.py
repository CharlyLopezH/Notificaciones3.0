from django.db import models

class Notificador(models.Model):
    nombres = models.CharField(max_length=100)
    apellido1 = models.CharField(max_length=100)
    apellido2 = models.CharField(max_length=100)
    telefono_emergencia = models.CharField(max_length=15)
    Codigo_Checador = models.IntegerField(null=True, blank=True, unique=True)
    fotografia = models.ImageField(upload_to='notificadores/fotos/', null=True, blank=True)    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    # 1-M RELATION: Reserva empleado/notificador a su respectiva área
    area = models.ForeignKey(
        'areas.Area', 
        on_delete=models.PROTECT, 
        related_name='notificadores',
        help_text="The functional organizational area this agent delivers documents for."
    )

    class Meta:
        db_table = 'notificadores'
        ordering = ['apellido1', 'apellido2', 'nombres']

    def __str__(self):
        return f"{self.apellido1} {self.apellido2}, {self.nombres} ({self.area.nombre_corto})"

    def nombre_completo(self):
        return f"{self.apellido1} {self.apellido2} {self.nombres}"

    def tiene_bitacoras(self):
        """Verifica si el notificador tiene bitácoras asociadas"""
        from notificaciones.bitacora.models import Bitacora
        return Bitacora.objects.filter(notificador=self).exists()