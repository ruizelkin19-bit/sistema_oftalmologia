from django import forms
from .models import Paciente, Departamento, Municipio

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = [
            'tipoDocumentoIdentificacion',
            'numDocumentoIdentificacion',
            'primer_nombre',
            'segundo_nombre',
            'primer_apellido',
            'segundo_apellido',
            'fechaNacimiento',
            'codSexo',
            'telefono',
            'correo',
            'direccion',
            'departamentoResidencia',
            'codMunicipioResidencia',
            'codPaisResidencia',
            'tipoUsuario',
            'regimen',  # nuevo
            'nivel',  # nuevo
            'ingreso_salarios_minimos',  # nuevo
            'clase_servicio',  # nuevo
            'codZonaTerritorialResidencia',
            'codPaisOrigen',
        ]

        widgets = {
            'tipoDocumentoIdentificacion': forms.Select(attrs={'class': 'form-select'}),
            'numDocumentoIdentificacion': forms.TextInput(attrs={'class': 'form-control'}),
            'primer_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'segundo_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'primer_apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'segundo_apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'fechaNacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'codSexo': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'departamentoResidencia': forms.Select(attrs={'class': 'form-control'}),
            'codMunicipioResidencia': forms.Select(attrs={'class': 'form-control'}),
            'codPaisResidencia': forms.Select(attrs={'class': 'form-control'}),
            'tipoUsuario': forms.Select(attrs={'class': 'form-control'}),
            'regimen': forms.Select(attrs={'class': 'form-select'}),
            'nivel': forms.Select(attrs={'class': 'form-select'}),
            'ingreso_salarios_minimos': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'clase_servicio': forms.Select(attrs={'class': 'form-select'}),
            'codZonaTerritorialResidencia': forms.Select(attrs={'class': 'form-control'}),
            'codPaisOrigen': forms.Select(attrs={'class': 'form-control'}),
        }

        labels = {
            'tipoDocumentoIdentificacion': 'Tipo de documento',
            'numDocumentoIdentificacion': 'Número de documento',
            'primer_nombre': 'Primer nombre',
            'segundo_nombre': 'Segundo nombre',
            'primer_apellido': 'Primer apellido',
            'segundo_apellido': 'Segundo apellido',
            'fechaNacimiento': 'Fecha de nacimiento',
            'codSexo': 'Sexo',
            'telefono': 'Teléfono',
            'correo': 'Correo electrónico',
            'direccion': 'Dirección',
            'departamentoResidencia': 'Departamento de residencia',
            'codMunicipioResidencia': 'Municipio de residencia',
            'codPaisResidencia': 'País de residencia',
            'tipoUsuario': 'Tipo de usuario',
            'regimen': 'Régimen de afiliación',
            'nivel': 'Nivel de ingresos',
            'ingreso_salarios_minimos': 'Ingreso aproximado (SM)',
            'clase_servicio': 'Clase de servicio',
            'codZonaTerritorialResidencia': 'Zona territorial de residencia',
            'codPaisOrigen': 'País de origen',
        }

    def __init__(self, *args, **kwargs):
        super(PacienteForm, self).__init__(*args, **kwargs)

        # Filtro dinámico de municipios por departamento
        if 'departamentoResidencia' in self.data:
            try:
                departamento_id = int(self.data.get('departamentoResidencia'))
                self.fields['codMunicipioResidencia'].queryset = Municipio.objects.filter(
                    departamento_id=departamento_id).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['codMunicipioResidencia'].queryset = Municipio.objects.none()
        elif self.instance.pk and self.instance.departamentoResidencia:
            self.fields['codMunicipioResidencia'].queryset = Municipio.objects.filter(
                departamento=self.instance.departamentoResidencia).order_by('nombre')
        else:
            self.fields['codMunicipioResidencia'].queryset = Municipio.objects.none()

        # Ajuste fechaNacimiento
        if self.instance and self.instance.fechaNacimiento:
            self.initial['fechaNacimiento'] = self.instance.fechaNacimiento.strftime('%Y-%m-%d')

        # Si el paciente ya tiene nivel/ingreso, mostrarlo
        if self.instance and self.instance.ingreso_salarios_minimos:
            self.initial['ingreso_salarios_minimos'] = self.instance.ingreso_salarios_minimos
        if self.instance and self.instance.nivel:
            self.initial['nivel'] = self.instance.nivel
