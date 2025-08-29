from django.contrib import admin
from .models import Soporte

@admin.register(Soporte)
class SoporteAdmin(admin.ModelAdmin):
    list_display = ("id", "numero_control", "tipo", "fecha_carga")  
    list_filter = ("tipo", "fecha_carga")
    search_fields = ("numero_control__numero_control", "descripcion")
