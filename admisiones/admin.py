# admisiones/admin.py

from django.contrib import admin
from .models import Admision

@admin.register(Admision)
class AdmisionAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'cita', 'fecha_admision')
    search_fields = ('paciente__nombre', 'cita__id')
    list_filter = ('fecha_admision',)
