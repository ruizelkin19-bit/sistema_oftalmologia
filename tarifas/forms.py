# tarifas/forms.py

from django import forms
from .models import Tarifa

class TarifaForm(forms.ModelForm):
    class Meta:
        model = Tarifa
        fields = ['codigo_cups', 'nombre', 'valor']
