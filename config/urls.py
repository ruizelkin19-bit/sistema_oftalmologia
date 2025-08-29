from django.contrib import admin
from django.urls import path, include
from .views import inicio
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', inicio, name='inicio'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    # Apps con namespace
    path('inventario/', include(('productos.urls', 'productos'), namespace='productos')),
    path('pacientes/', include(('pacientes.urls', 'pacientes'), namespace='pacientes')),
    path('citas/', include(('citas.urls', 'citas'), namespace='citas')),
    path('historias/', include(('historias.urls', 'historias'), namespace='historias')),
    path('rips/', include(('rips.urls', 'rips'), namespace='rips')),
    path('informes/', include(('informes.urls', 'informes'), namespace='informes')),
    path('facturacion/', include(('facturacion.urls', 'facturacion'), namespace='facturacion')),
    path('tarifas/', include(('tarifas.urls', 'tarifas'), namespace='tarifas')),
    path('admisiones/', include(('admisiones.urls', 'admisiones'), namespace='admisiones')),
    path('soportes/', include(('soportes.urls', 'soportes'), namespace='soportes')),
]


# al final del archivo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)