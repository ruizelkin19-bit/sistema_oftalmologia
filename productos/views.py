from django.shortcuts import render
from .models import Producto

def listado_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos/listado.html', {'productos': productos})
