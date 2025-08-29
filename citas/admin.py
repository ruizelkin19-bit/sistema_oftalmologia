from django.contrib import admin
from .models import Cita

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'fecha', 'hora', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('paciente__nombre', 'paciente__documento')
    ordering = ('-fecha', '-hora')
