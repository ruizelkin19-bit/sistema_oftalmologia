from django import forms
from .models import Soporte

class SoporteForm(forms.ModelForm):
    class Meta:
        model = Soporte
        fields = ['tipo', 'archivo', 'descripcion']
        labels = {
            'tipo': 'Tipo de soporte',
            'archivo': 'Archivo',
            'descripcion': 'Descripción (opcional)',
        }
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
