from django.urls import path
from . import views

app_name = 'historias'

urlpatterns = [
    # Listado general de historias clínicas
    path('', views.listado_historias, name='listado_historias'),

    # Crear historia clínica desde una cita
    path('crear/<int:cita_id>/', views.crear_historia_clinica, name='crear_historia_clinica'),

    # Ver historia clínica (por ID de la historia)
    path('historia/<int:historia_id>/', views.ver_historia_clinica, name='ver_historia_clinica'),

    # Editar historia clínica (por ID de la historia)
    path('historia/<int:pk>/editar/', views.editar_historia_clinica, name='editar_historia_clinica'),

    # Detalle adicional (si necesitas una vista separada del "ver")
    path('detalle/<int:pk>/', views.detalle_historia, name='detalle_historia'),

    # Ingreso desde cita (crea historia clínica e ingresa al paciente)
    path('ingresar/<int:cita_id>/', views.ingresar_paciente, name='ingresar_paciente'),

    # Dar ingreso desde cita directamente
    path('dar_ingreso/<int:cita_id>/', views.dar_ingreso, name='dar_ingreso'),

    # Dar ingreso usando documento del paciente
    path('ingreso/documento/<str:documento>/', views.dar_ingreso, name='dar_ingreso_por_documento'),

    path('atender/<int:admision_id>/', views.atender, name='atender'),

    path('<int:historia_id>/pdf/', views.generar_historia_pdf, name='generar_pdf'),
]
