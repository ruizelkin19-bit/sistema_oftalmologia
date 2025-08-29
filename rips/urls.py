from django.urls import path
from . import views

app_name = 'rips'

urlpatterns = [
    path('facturas/', views.listado_rips, name='listado_rips'),  # <-- el nombre es 'listado_rips', no 'listado_facturas'
    path('exportar_us/', views.exportar_us, name='exportar_us'),
]

