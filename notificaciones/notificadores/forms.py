# notificaciones/notificadores/forms.py
from django import forms
from .models import Notificador
from notificaciones.areas.models import Area

class NotificadorForm(forms.ModelForm):
    class Meta:
        model = Notificador
        fields = ['nombres', 'apellido1', 'apellido2', 'telefono_emergencia', 
                  'Codigo_Checador', 'fotografia', 'area']
        widgets = {
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Juan Carlos'
            }),
            'apellido1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Pérez'
            }),
            'apellido2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: González (opcional)'
            }),
            'telefono_emergencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 555-1234567'
            }),
            'Codigo_Checador': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: NOT-001'
            }),
            'fotografia': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'area': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'nombres': 'Nombres *',
            'apellido1': 'Apellido Paterno *',
            'apellido2': 'Apellido Materno',
            'telefono_emergencia': 'Teléfono de Emergencia',
            'Codigo_Checador': 'Código Checador',
            'fotografia': 'Fotografía',
            'area': 'Área de Adscripción *',
        }
        help_texts = {
            'Codigo_Checador': 'Código único para registro de asistencia',
            'fotografia': 'Formatos permitidos: JPG, PNG (máx 5MB)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Marcar campos como requeridos
        self.fields['nombres'].required = True
        self.fields['apellido1'].required = True
        self.fields['area'].required = True
        
        # Ordenar áreas por nombre
        self.fields['area'].queryset = Area.objects.all().order_by('nombre_corto')

        