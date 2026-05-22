# notificaciones/bitacora/models.py
from django.db import models
from datetime import date

class Bitacora(models.Model):
    # Opciones para el campo situacion (catálogo)
    SITUACION_ASIGNADA = 'Asignada'
    SITUACION_EN_RUTA = 'En Ruta'
    SITUACION_ENTREGADA = 'Entregada'
    SITUACION_CANCELADA = 'Cancelada'
    SITUACION_PENDIENTE = 'Pendiente'
    
    SITUACIONES = [
        (SITUACION_ASIGNADA, 'Asignada'),
        (SITUACION_EN_RUTA, 'En Ruta'),
        (SITUACION_ENTREGADA, 'Entregada'),
        (SITUACION_CANCELADA, 'Cancelada'),
        (SITUACION_PENDIENTE, 'Pendiente'),
    ]
    
    # Constantes para estados visuales (calculados)
    ESTADO_VISUAL_ASIGNADA = 'asignada'
    ESTADO_VISUAL_EN_RUTA = 'en_ruta'
    ESTADO_VISUAL_EXPIRANDO = 'expirando'
    ESTADO_VISUAL_EXPIRADA = 'expirada'
    ESTADO_VISUAL_ENTREGADA = 'entregada'
    
    # Campos de la tabla
    oficio_memo = models.CharField(max_length=100)
    situacion = models.CharField(
        max_length=20, 
        choices=SITUACIONES, 
        default=SITUACION_ASIGNADA
    )
    fecha_bitacora = models.DateField()
    fecha_termino = models.DateField()
    destinatario = models.CharField(max_length=255)
    expediente_asunto = models.TextField()
    fecha_acuse = models.DateField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    pdf_adjunto = models.FileField(
        upload_to='pdfs/',
        null=True, 
        blank=True,
        help_text='Solo archivos PDF'
    )
    capturo = models.CharField(max_length=20, blank=True)
    notificador = models.ForeignKey(
        'notificadores.Notificador',
        on_delete=models.RESTRICT,
        related_name='bitacora'
    )
    
    class Meta:
        db_table = 'bitacora'
        ordering = ['fecha_termino']
    
    def __str__(self):
        return f"{self.oficio_memo} — {self.destinatario}"
    
    def get_estado_visual(self):
        """Calcula el estado visual (color) basado en situación y fechas"""
        hoy = date.today()
        
        # Si está entregada
        if self.situacion == self.SITUACION_ENTREGADA:
            return self.ESTADO_VISUAL_ENTREGADA
        
        # Si la fecha de término ya pasó
        if self.fecha_termino < hoy:
            return self.ESTADO_VISUAL_EXPIRADA
        
        # Si es hoy o mañana la fecha de término
        dias_restantes = (self.fecha_termino - hoy).days
        if dias_restantes <= 1:
            return self.ESTADO_VISUAL_EXPIRANDO
        
        # Según la situación actual
        if self.situacion == self.SITUACION_EN_RUTA:
            return self.ESTADO_VISUAL_EN_RUTA
        
        return self.ESTADO_VISUAL_ASIGNADA
    
    def get_color_estado(self):
        """Retorna la clase CSS para el color del estado visual"""
        colores = {
            self.ESTADO_VISUAL_ASIGNADA: 'bg-primary',
            self.ESTADO_VISUAL_EN_RUTA: 'bg-info',
            self.ESTADO_VISUAL_EXPIRANDO: 'bg-warning',
            self.ESTADO_VISUAL_EXPIRADA: 'bg-danger',
            self.ESTADO_VISUAL_ENTREGADA: 'bg-success',
        }
        return colores.get(self.get_estado_visual(), 'bg-secondary')
    
    def get_texto_estado(self):
        """Retorna el texto legible del estado visual"""
        textos = {
            # self.ESTADO_VISUAL_ASIGNADA: '📋 Asignada',
            # self.ESTADO_VISUAL_EN_RUTA: '🚚 En Ruta',
            # self.ESTADO_VISUAL_EXPIRANDO: '⚠️ Expirando',
            # self.ESTADO_VISUAL_EXPIRADA: '❌ Expirada',
            # self.ESTADO_VISUAL_ENTREGADA: '✅ Entregada',

            self.ESTADO_VISUAL_ASIGNADA: 'Asignada',
            self.ESTADO_VISUAL_EN_RUTA: 'En Ruta',
            self.ESTADO_VISUAL_EXPIRANDO: 'Expirando',
            self.ESTADO_VISUAL_EXPIRADA: 'Expirada',
            self.ESTADO_VISUAL_ENTREGADA: 'Entregada',




        }
        return textos.get(self.get_estado_visual(), 'Desconocido')
    
    @property
    def dias_restantes(self):
        """Calcula días restantes para la fecha de término"""
        if self.situacion == self.SITUACION_ENTREGADA:
            return 0
        hoy = date.today()
        if self.fecha_termino >= hoy:
            return (self.fecha_termino - hoy).days
        return 0
    
    @property
    def esta_retrasada(self):
        """Indica si la notificación está fuera de término"""
        return self.situacion != self.SITUACION_ENTREGADA and self.fecha_termino < date.today()