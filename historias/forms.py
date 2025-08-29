from django import forms
from .models import HistoriaClinica

class HistoriaClinicaForm(forms.ModelForm):
    class Meta:
        model = HistoriaClinica
        exclude = ['paciente', 'cita']  # <- Ocultamos estos campos del formulario
        widgets = {
            # --- Datos personales ---
            'ocupacion': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),

            # --- Motivo y antecedentes ---
            'motivo_consulta': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'enfermedad_actual': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'antecedentes_personales': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'antecedentes_familiares': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'antecedentes_medicos': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'antecedentes_quirurgicos': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'antecedentes_oftalmologicos': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'medicamentos_actuales': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'alergias': forms.TextInput(attrs={'class': 'form-control'}),

            # --- Signos vitales ---
            'tension_arterial': forms.TextInput(attrs={'class': 'form-control'}),
            'frecuencia_cardiaca': forms.TextInput(attrs={'class': 'form-control'}),

            # --- Agudeza visual ---
            'av_sin_correccion_od': forms.TextInput(attrs={'class': 'form-control'}),
            'av_sin_correccion_oi': forms.TextInput(attrs={'class': 'form-control'}),
            'av_con_correccion_od': forms.TextInput(attrs={'class': 'form-control'}),
            'av_con_correccion_oi': forms.TextInput(attrs={'class': 'form-control'}),
            'av_estenopeico_od': forms.TextInput(attrs={'class': 'form-control'}),
            'av_estenopeico_oi': forms.TextInput(attrs={'class': 'form-control'}),

            # --- Refracción ---
            'refraccion_subjetiva_od': forms.TextInput(attrs={'class': 'form-control'}),
            'refraccion_subjetiva_oi': forms.TextInput(attrs={'class': 'form-control'}),
            'refraccion_objetiva_od': forms.TextInput(attrs={'class': 'form-control'}),
            'refraccion_objetiva_oi': forms.TextInput(attrs={'class': 'form-control'}),
            'refraccion_final_od': forms.TextInput(attrs={'class': 'form-control'}),
            'refraccion_final_oi': forms.TextInput(attrs={'class': 'form-control'}),

            # --- Examen ocular ---
            'anexos_oculares': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'segmento_anterior': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'segmento_posterior': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'pupilas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'motilidad_ocular': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'reflejos_pupilares': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'fondo_de_ojo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'presion_intraocular_od': forms.TextInput(attrs={'class': 'form-control'}),
            'presion_intraocular_oi': forms.TextInput(attrs={'class': 'form-control'}),

            # --- Pruebas complementarias ---
            'campimetria_visual': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'vision_colores': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'estereopsis': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),

            # --- Diagnóstico y tratamiento ---
            'diagnostico_principal': forms.TextInput(attrs={'class': 'form-control'}),
            'diagnostico_secundario': forms.TextInput(attrs={'class': 'form-control'}),
            'cie10_principal': forms.TextInput(attrs={'class': 'form-control'}),
            'diagnosticos_cie10': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'plan_tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'conducta': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),

            # --- Médico tratante ---
            'firmado_por': forms.TextInput(attrs={'class': 'form-control'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control'}),
            'registro_medico': forms.TextInput(attrs={'class': 'form-control'}),
            'firma_digital': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),

            # --- Otros ---
            'numero_control': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }
