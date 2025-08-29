from django.shortcuts import render, redirect, get_object_or_404
from .models import Tarifa
from .forms import TarifaForm
from django.contrib import messages

def listar_tarifas(request):
    tarifas = Tarifa.objects.all()
    return render(request, 'tarifas/listado_tarifas.html', {'tarifas': tarifas})

def crear_tarifa(request):
    if request.method == 'POST':
        form = TarifaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarifa creada exitosamente.')
            return redirect('listar_tarifas')
    else:
        form = TarifaForm()
    return render(request, 'tarifas/form_tarifa.html', {'form': form})

def editar_tarifa(request, tarifa_id):
    tarifa = get_object_or_404(Tarifa, id=tarifa_id)
    if request.method == 'POST':
        form = TarifaForm(request.POST, instance=tarifa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarifa actualizada correctamente.')
            return redirect('listar_tarifas')
    else:
        form = TarifaForm(instance=tarifa)
    return render(request, 'tarifas/form_tarifa.html', {'form': form})

def eliminar_tarifa(request, tarifa_id):
    tarifa = get_object_or_404(Tarifa, id=tarifa_id)
    if request.method == 'POST':
        tarifa.delete()
        messages.success(request, 'Tarifa eliminada correctamente.')
        return redirect('listar_tarifas')
    return render(request, 'tarifas/confirmar_eliminar_tarifa.html', {'tarifa': tarifa})
