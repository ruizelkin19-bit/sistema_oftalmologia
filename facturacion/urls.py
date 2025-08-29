from django.urls import path
from . import views

app_name = 'facturacion'

urlpatterns = [
    path('', views.listado_facturas, name='listado_facturas'),
    path('listar/', views.listado_facturas, name='listado_facturas_listar'),
    path('buscar-cita/', views.buscar_cita, name='buscar_cita'),
    path('facturar/<int:cita_id>/', views.facturar_cita, name='facturar_cita'),  # <--- esta es la clave
    path('detalle/<int:factura_id>/', views.detalle_factura, name='detalle_factura'),
    path('factura/pdf/<int:factura_id>/', views.generar_factura_pdf, name='generar_factura_pdf'),
]
