from django.contrib import admin
from .models import Tarifa, Cie10

@admin.register(Tarifa)
class TarifaAdmin(admin.ModelAdmin):
    list_display = ('codigo_cups', 'nombre', 'valor', 'activo')
    search_fields = ('codigo_cups', 'nombre')
    list_filter = ('activo',)

@admin.register(Cie10)
class Cie10Admin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion')
    search_fields = ('codigo',)
