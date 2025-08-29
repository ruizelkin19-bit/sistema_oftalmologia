from django import forms
from .models import Admision
from pacientes.models import Paciente
from citas.models import Cita


class AdmisionForm(forms.ModelForm):
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.all(),
        label="Paciente",
        required=False,
        disabled=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cita = forms.ModelChoiceField(
        queryset=Cita.objects.all(),
        label="Cita",
        required=False,
        widget=forms.HiddenInput()  # 👈 Guardamos el id oculto
    )
    cita_display = forms.CharField(  # 👈 Solo para mostrar el CUPS
        label="Cita",
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'true'})
    )
    tipo_usuario = forms.CharField(
        label="Tipo usuario",
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    regimen = forms.CharField(
        label="Régimen",
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Admision
        fields = [
            'paciente',
            'cita',
            'tipo_usuario',
            'regimen',
            'entidad_responsable',
            'numero_autorizacion',
            'motivo_consulta',
            'remitido_por',
            'diagnostico_presuntivo',
            'observaciones',
        ]
        widgets = {
            'entidad_responsable': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_autorizacion': forms.TextInput(attrs={'class': 'form-control'}),
            'motivo_consulta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'remitido_por': forms.TextInput(attrs={'class': 'form-control'}),
            'diagnostico_presuntivo': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        cita = kwargs.pop('cita', None)  # Obtener cita si se pasa desde la vista
        super().__init__(*args, **kwargs)

        if cita:
            # Solo permitir esa cita
            self.fields['cita'].queryset = Cita.objects.filter(id=cita.id)
            self.initial['cita'] = cita.id  # 👈 Guardar el id

            # Mostrar el nombre del CUPS en campo aparte
            self.fields['cita_display'].initial = cita.codigo_cups.nombre

            # Paciente asociado
            self.fields['paciente'].queryset = Paciente.objects.filter(id=cita.paciente.id)
            self.initial['paciente'] = cita.paciente

            # Tipo usuario y régimen del paciente
            if hasattr(cita.paciente, 'get_tipoUsuario_display'):
                self.initial['tipo_usuario'] = cita.paciente.tipoUsuario
            self.initial['regimen'] = cita.paciente.get_regimen_display()

            # Asignamos paciente al instance
            self.instance.paciente = cita.paciente
        else:
            # Si no hay cita, lista las "Agendadas"
            self.fields['cita'].queryset = Cita.objects.filter(estado='Agendada')
