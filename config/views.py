# views.py (en app o en config principal)
from django.shortcuts import render
from datetime import datetime

def inicio(request):
    return render(request, 'inicio.html', {'year': datetime.now().year})
