from django.db import models
from pacientes.models import Paciente
from citas.models import Cita
from django.utils import timezone
from django.core.exceptions import ValidationError

class Admision(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('admitido', 'Admitido'),
        ('atendido', 'Atendido'),
        ('cancelado', 'Cancelado'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE)
    fecha_admision = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    numero_control = models.CharField(max_length=50, unique=True, blank=True, editable=False)

    # Campos administrativos y clínicos
    entidad_responsable = models.CharField(max_length=100, blank=True, null=True, help_text="Nombre de EPS o entidad que autoriza")
    numero_autorizacion = models.CharField(max_length=30, blank=True, null=True)
    motivo_consulta = models.TextField(blank=True, null=True)
    remitido_por = models.CharField(max_length=100, blank=True, null=True)
    diagnostico_presuntivo = models.CharField(max_length=255, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Admisión {self.numero_control} - {self.paciente.nombre}"

    def save(self, *args, **kwargs):
        # Asignar el número de control desde la factura si no está definido
        if not self.numero_control and hasattr(self.cita, 'factura'):
            self.numero_control = self.cita.factura.numero_control
        super().save(*args, **kwargs)

    def clean(self):
        # Validar que no exista otra admisión con la misma cita
        if Admision.objects.exclude(pk=self.pk).filter(cita=self.cita).exists():
            raise ValidationError({'cita': 'Esta cita ya tiene una admisión registrada.'})

        # Validar que la cita no tenga un estado diferente de "Agendada" si la admisión es nueva
        if self.estado == 'admitido' and self.cita.estado != 'Agendada':
            raise ValidationError({'cita': 'La cita debe estar en estado "Agendada" para ser admitida.'})

    @property
    def historia(self):
        from historias.models import HistoriaClinica
        return HistoriaClinica.objects.filter(numero_control=self.numero_control).first()

    def actualizar_estado_cita(self):
        """ Actualizar el estado de la cita a 'Admitida' cuando se crea la admisión """
        if self.cita and self.estado == 'admitido':
            self.cita.estado = 'Admitida'
            self.cita.save()
