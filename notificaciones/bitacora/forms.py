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
            # 'capturo' ← se llena automáticamente después
        ]
        
        widgets = {
            'fecha_bitacora': forms.DateInput(
                attrs={'type': 'date', 
                       'class':'form-control',
                       'readonly': 'readonly',    
                       'value': date.today().strftime('%Y-%m-%d')                   
                       }
                ),
            'fecha_termino': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_acuse': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expediente_asunto': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'oficio_memo': forms.TextInput(attrs={'class': 'form-control'}),
            'destinatario': forms.TextInput(attrs={'class': 'form-control'}),
            'notificador': forms.Select(attrs={'class': 'form-select'}),
            'situacion': forms.Select(attrs={'class': 'form-select'}),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if not self.instance.pk:  # Solo para nuevos registros
                self.initial['fecha_bitacora'] = date.today()

    
    
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
        
        return cleaned_data