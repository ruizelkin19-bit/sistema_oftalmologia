from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = "soportes"

urlpatterns = [
    path("", lambda request: redirect("soportes:lista_numeros_control")),
    path("numeros-control/", views.lista_numeros_control, name="lista_numeros_control"),
    path('<str:numero_control>/visor/', views.visor_soporte, name='visor_soporte'),
    path('<str:numero_control>/cargar/', views.cargar_soporte, name='cargar_soporte'),
    path("<str:numero_control>/descargar/", views.descargar_paquete, name="descargar_paquete"),
    path('eliminar/<int:soporte_id>/', views.eliminar_soporte, name='eliminar_soporte'),
]
