# informes/forms.py

from django import forms

class FiltroFechaForm(forms.Form):
    fecha_inicio = forms.DateField(label="Desde", required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    fecha_fin = forms.DateField(label="Hasta", required=True, widget=forms.DateInput(attrs={'type': 'date'}))
