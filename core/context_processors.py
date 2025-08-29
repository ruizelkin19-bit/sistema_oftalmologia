# core/context_processors.py
from django.conf import settings

def ips_config(request):
    """Pasa los datos de la IPS a todas las plantillas"""
    return {"IPS_CONFIG": settings.IPS_CONFIG}
