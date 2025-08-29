from django.urls import path
from . import views

app_name = 'pacientes'

urlpatterns = [
    path('', views.buscar_paciente, name='buscar_paciente'),
    path('crear/', views.crear_paciente, name='crear_paciente'),
    path('<int:pk>/', views.detalle_paciente, name='detalle_paciente'),
    path('<int:pk>/editar/', views.editar_paciente, name='editar_paciente'),
    path('<int:pk>/eliminar/', views.eliminar_paciente, name='eliminar_paciente'),
    path('ajax/cargar-municipios/', views.cargar_municipios, name='ajax_cargar_municipios'),
    path('admitir/<int:cita_id>/', views.admitir_paciente, name='admitir_paciente'),
]
