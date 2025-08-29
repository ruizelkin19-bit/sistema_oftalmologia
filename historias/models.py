from django.db import models
from pacientes.models import Paciente
from citas.models import Cita
from tarifas.models import Cie10
from admisiones.models import Admision


class HistoriaClinica(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE)
    admision = models.OneToOneField(
        Admision,
        on_delete=models.CASCADE,
        related_name="historia_clinica",
        null=True,
        blank=True
    )

    numero_control = models.CharField(
        max_length=50, unique=True, editable=False, blank=True
    )
    fecha = models.DateField(auto_now_add=True)

    # Datos Generales
    ocupacion = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    # Motivo y antecedentes
    motivo_consulta = models.TextField(blank=True, null=True)
    enfermedad_actual = models.TextField(blank=True, null=True)
    antecedentes_personales = models.TextField(blank=True, null=True)
    antecedentes_familiares = models.TextField(blank=True, null=True)
    antecedentes_medicos = models.TextField(blank=True, null=True)
    antecedentes_quirurgicos = models.TextField(blank=True, null=True)
    antecedentes_oftalmologicos = models.TextField(blank=True, null=True)
    medicamentos_actuales = models.TextField(blank=True, null=True)
    alergias = models.CharField(max_length=255, blank=True, null=True)

    # Signos vitales
    tension_arterial = models.CharField("Tensión arterial", max_length=20, blank=True, null=True)
    frecuencia_cardiaca = models.CharField("Frecuencia cardíaca", max_length=20, blank=True, null=True)

    # Agudeza visual
    av_sin_correccion_od = models.CharField("AV sin corrección OD", max_length=50, blank=True, null=True)
    av_sin_correccion_oi = models.CharField("AV sin corrección OI", max_length=50, blank=True, null=True)
    av_con_correccion_od = models.CharField("AV con corrección OD", max_length=50, blank=True, null=True)
    av_con_correccion_oi = models.CharField("AV con corrección OI", max_length=50, blank=True, null=True)
    av_estenopeico_od = models.CharField("AV estenopeico OD", max_length=50, blank=True, null=True)
    av_estenopeico_oi = models.CharField("AV estenopeico OI", max_length=50, blank=True, null=True)

    # Refracción
    refraccion_subjetiva_od = models.CharField("Refracción subjetiva OD", max_length=100, blank=True, null=True)
    refraccion_subjetiva_oi = models.CharField("Refracción subjetiva OI", max_length=100, blank=True, null=True)
    refraccion_objetiva_od = models.CharField("Refracción objetiva OD", max_length=100, blank=True, null=True)
    refraccion_objetiva_oi = models.CharField("Refracción objetiva OI", max_length=100, blank=True, null=True)
    refraccion_final_od = models.CharField("Refracción final OD", max_length=100, blank=True, null=True)
    refraccion_final_oi = models.CharField("Refracción final OI", max_length=100, blank=True, null=True)

    # Examen físico ocular
    anexos_oculares = models.TextField(blank=True, null=True)
    segmento_anterior = models.TextField(blank=True, null=True)
    segmento_posterior = models.TextField(blank=True, null=True)
    pupilas = models.TextField(blank=True, null=True)
    motilidad_ocular = models.TextField(blank=True, null=True)
    reflejos_pupilares = models.TextField(blank=True, null=True)
    fondo_de_ojo = models.TextField(blank=True, null=True)

    presion_intraocular_od = models.CharField("Presión intraocular OD", max_length=10, blank=True, null=True)
    presion_intraocular_oi = models.CharField("Presión intraocular OI", max_length=10, blank=True, null=True)

    # Pruebas complementarias
    campimetria_visual = models.TextField(blank=True, null=True)
    vision_colores = models.TextField("Test de Ishihara", blank=True, null=True)
    estereopsis = models.TextField(blank=True, null=True)

    # Diagnóstico y plan
    diagnostico_principal = models.CharField("Diagnóstico principal", max_length=255, blank=True, null=True)
    diagnostico_secundario = models.CharField("Diagnóstico secundario", max_length=255, blank=True, null=True)
    cie10_principal = models.CharField("Código CIE10 principal", max_length=20, blank=True, null=True)
    diagnosticos_cie10 = models.ManyToManyField(
        Cie10, blank=True, related_name='historias', verbose_name="Diagnósticos adicionales CIE10"
    )

    plan_tratamiento = models.TextField(blank=True, null=True)
    conducta = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    # Profesional tratante
    firmado_por = models.CharField("Nombre del profesional", max_length=255, blank=True, null=True)
    especialidad = models.CharField("Especialidad", max_length=100, blank=True, null=True)
    registro_medico = models.CharField("Registro Médico (RM)", max_length=100, blank=True, null=True)
    firma_digital = models.TextField(blank=True, null=True)

    creado_en = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.admision and not self.numero_control:
            self.numero_control = self.admision.numero_control
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Historia Clínica: {self.numero_control}"
