# citas/models.py

from django.db import models
from pacientes.models import Paciente
from tarifas.models import Tarifa
from django.utils import timezone

class Cita(models.Model):
    ESTADOS_CHOICES = [
        ('Agendada', 'Agendada'),
        ('Cancelada', 'Cancelada'),
        ('Atendida', 'Atendida'),
    ]
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.TextField()
    codigo_cups = models.ForeignKey(Tarifa, on_delete=models.SET_NULL, null=True, blank=False)
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default='Agendada')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Muestra: "2025-08-26 10:00 - Nombre del CUPS"
        cups_nombre = self.codigo_cups.nombre if self.codigo_cups else "Sin CUPS"
        return f"{self.fecha} {self.hora.strftime('%H:%M')} - {cups_nombre}"
