# pacientes/forms_excel.py

from django import forms

class CargarExcelPacientesForm(forms.Form):
    archivo_excel = forms.FileField(label="Seleccione el archivo Excel")
