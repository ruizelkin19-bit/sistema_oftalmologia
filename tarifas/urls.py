from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_tarifas, name='listar_tarifas'),
    path('nueva/', views.crear_tarifa, name='crear_tarifa'),
    path('editar/<int:tarifa_id>/', views.editar_tarifa, name='editar_tarifa'),
    path('eliminar/<int:tarifa_id>/', views.eliminar_tarifa, name='eliminar_tarifa'),
]
