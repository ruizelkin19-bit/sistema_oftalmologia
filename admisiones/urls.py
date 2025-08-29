from django.urls import path
from . import views

app_name = 'admisiones'

urlpatterns = [
    path('crear/', views.crear_admision, name='crear_admision'),
    path('listado/', views.listado_admisiones, name='listado_admisiones'),
    path('<int:admision_id>/atender/', views.marcar_atendido, name='marcar_atendido'),
    path('<int:admision_id>/', views.ver_admision, name='ver_admision'),
    path('<int:admision_id>/pdf/', views.generar_admision_pdf, name='generar_pdf'),
]
