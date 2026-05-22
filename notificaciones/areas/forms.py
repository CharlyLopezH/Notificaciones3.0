from django import forms
from .models import Area

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['nombre', 'nombre_corto', 'extension_telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Nombre de dirección'}),
            'nombre_corto': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Ej. JUR'}),
            'extension_telefono': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Ej. 101'}),
        }
