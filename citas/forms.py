# citas/forms.py

from django import forms
from .models import Cita
from pacientes.models import Paciente
from tarifas.models import Tarifa

class CitaForm(forms.ModelForm):
    documento = forms.CharField(
        label="Documento del paciente",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Cita
        fields = ['documento', 'codigo_cups', 'fecha', 'hora', 'motivo']
        widgets = {
            'codigo_cups': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        if not Paciente.objects.filter(numDocumentoIdentificacion=documento).exists():
            raise forms.ValidationError("No existe un paciente con ese documento.")
        return documento
