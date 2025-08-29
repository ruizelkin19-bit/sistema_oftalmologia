# historias/admin.py

from django.contrib import admin
from .models import HistoriaClinica
from admisiones.models import Admision

@admin.register(HistoriaClinica)
class HistoriaClinicaAdmin(admin.ModelAdmin):
    list_display = ('numero_control', 'paciente', 'fecha', 'diagnostico_principal')  # ← corregido
    search_fields = ('paciente__nombre', 'numero_control', 'diagnostico_principal')
    list_filter = ('fecha', 'especialidad')
    ordering = ('-fecha',)
