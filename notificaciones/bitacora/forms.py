# notificaciones/bitacora/forms.py
from datetime import date


from django import forms
from .models import Bitacora

class BitacoraForm(forms.ModelForm):
    class Meta:
        model = Bitacora
        fields = [
            'oficio_memo',
            'situacion',
            'fecha_bitacora',
            'fecha_termino',
            'destinatario',
            'expediente_asunto',
            'fecha_acuse',
            'pdf_adjunto',
            'notificador',
            'capturo', 
        ]
        
        widgets = {
            'fecha_bitacora': forms.DateInput(
                attrs={'type': 'date', 
                       'class':'form-control',
                    #    'readonly': 'readonly',    
                    #    'value': date.today().strftime('%Y-%m-%d')                   
                       }
                ),
            'fecha_termino': forms.DateInput(
                attrs={'type': 'date', 
                       'class': 'form-control'
                       }
                ),
            'fecha_acuse': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expediente_asunto': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'oficio_memo': forms.TextInput(attrs={'class': 'form-control'}),
            'destinatario': forms.TextInput(attrs={'class': 'form-control'}),
            'notificador': forms.Select(attrs={'class': 'form-select'}),
            'situacion': forms.Select(attrs={'class': 'form-select'}),
            'capturo': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # ← Extraer user
        super().__init__(*args, **kwargs)  # ← Llamar al padre
        
        # Establecer fecha actual para nuevos registros
            # Establecer fecha actual para NUEVOS registros
        self.fields['fecha_bitacora'].required = False
        if not self.instance.pk:  # Si es CREACIÓN 
            self.fields['fecha_bitacora'].widget.attrs['readonly'] = 'readonly'            
            today = date.today().strftime('%Y-%m-%d')
            self.initial['fecha_bitacora'] = today
            # También hacer el campo de solo lectura            
            self.fields['fecha_bitacora'].required = False
        else:
        # Para EDICIÓN: mostrar la fecha existente (sin readonly)
            if 'fecha_bitacora' in self.fields:
                self.fields['fecha_bitacora'].widget.attrs.pop('readonly', None)            
                # self.fields['fecha_termino'].widget.attrs.pop('readonly', None)  #Redundante
                
        
        # Filtrar notificadores según el rol del usuario
        if user:
            self.fields['capturo'].initial = user.username
            self.fields['capturo'].disabled = True  # Deshabilitar completamente
            from notificaciones.notificadores.models import Notificador
            
            if user.rol == 'coordinador' and user.area:
                self.fields['notificador'].queryset = Notificador.objects.filter(area=user.area)

            elif user.rol == 'admin' and user.area:  # ← admin
                self.fields['notificador'].queryset = Notificador.objects.filter(area=user.area)

            elif user.rol == 'notificador' and user.codigo_checador:
                empleado = Notificador.objects.filter(Codigo_Checador=str(user.codigo_checador)).first()
                if empleado:
                    self.fields['notificador'].queryset = Notificador.objects.filter(id=empleado.id)
            else:
                self.fields['notificador'].queryset = Notificador.objects.all()

    def clean_pdf_adjunto(self):
        pdf = self.cleaned_data.get('pdf_adjunto')
        if pdf and not pdf.name.endswith('.pdf'):
            raise forms.ValidationError('Solo se permiten archivos PDF')
        return pdf
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_bitacora = cleaned_data.get('fecha_bitacora')
        fecha_termino = cleaned_data.get('fecha_termino')
        
        if fecha_bitacora and fecha_termino and fecha_termino < fecha_bitacora:
            raise forms.ValidationError('La fecha de término no puede ser menor a la fecha de bitácora')


#Activación de los formularios para actualización de situación
class CambioSituacionForm(forms.Form):
    nueva_situacion = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Nueva Situación"
    )
    fecha_real = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'form-control',
            'value': date.today().strftime('%Y-%m-%d')  # ← Valor por defecto
        }),
        label="Fecha de la actuación",        
        initial=date.today  # ← Esto mostrará la fecha de hoy por defecto
    )
    notas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        label="Notas / Observaciones",
        help_text="Obligatorio si la nueva situación es 'Cancelada' o 'No Entregada'"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Bitacora
        self.fields['nueva_situacion'].choices = Bitacora.SITUACIONES
    
    def clean(self):
        cleaned_data = super().clean()
        nueva_situacion = cleaned_data.get('nueva_situacion')
        notas = cleaned_data.get('notas')
        
        if nueva_situacion in ['Cancelada', 'No Entregada'] and not notas:
            raise forms.ValidationError('Las notas son obligatorias cuando la situación es Cancelada o No Entregada')

        return cleaned_data