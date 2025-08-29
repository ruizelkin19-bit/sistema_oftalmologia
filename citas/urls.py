# citas/urls.py

from django.urls import path
from . import views

app_name = 'citas'

urlpatterns = [
    path('', views.listado_citas, name='listado_citas'),
    path('crear/', views.crear_cita, name='crear_cita'),

    # Vistas de agenda
    path('agenda/', views.agenda_disponible, name='agenda_disponible'),
    path('agenda/calendario/', views.agenda_calendario, name='agenda_calendario'),
    path('agenda-semanal/', views.agenda_semanal, name='agenda_semanal'),

    # Agenda mensual
    path('agenda-mes/', views.agenda_mes, name='agenda_mes'),
    path('agenda-mensual/<int:year>/<int:month>/', views.agenda_mes, name='agenda_mes_mes'),

    # Agenda diaria con parámetro fecha obligatorio en la URL
    path('agenda/<int:anio>/<int:mes>/<int:dia>/', views.agenda_dia, name='agenda_dia'),
    path('', views.listado_citas, name='listado_citas'),
    path('editar/<int:cita_id>/', views.editar_cita, name='editar_cita'),  # 👈 esta línea es la que faltaba
    path('cancelar/<int:cita_id>/', views.cancelar_cita, name='cancelar_cita'),
    path('admitir/<int:cita_id>/', views.admitir_paciente, name='admitir_paciente'),
]
