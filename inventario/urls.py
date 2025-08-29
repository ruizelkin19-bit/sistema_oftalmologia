from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.listado_inventario, name='listado_inventario'),  # La ruta con ese name
    # otras rutas aquí...
]
