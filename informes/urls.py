from django.urls import path
from . import views

app_name = 'informes'

urlpatterns = [
    path('', views.listado_informes, name='listado_informes'),
    path('exportar/<str:modulo>/', views.exportar_excel, name='exportar_excel'),
    path('traza/<str:numero_control>/', views.informe_traza, name='informe_traza'),
]
