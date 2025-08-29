from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime
from .models import Paciente
from citas.models import Cita
from .forms import PacienteForm
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from historias.models import HistoriaClinica  # Import corregido
from pacientes.models import Municipio
from datetime import datetime, date  # << Incluye 'date'
from django.views.decorators.http import require_POST

# Buscar paciente por número de documento
def buscar_paciente(request):
    documento = request.GET.get('documento')
    paciente = None
    cita = None

    if documento:
        try:
            paciente = Paciente.objects.get(numDocumentoIdentificacion=documento)
            hoy = timezone.localdate()
            # Filtrar solo la cita agendada para hoy
            cita = (
            Cita.objects.filter(
                paciente=paciente,
                fecha__gte=date.today(),
                estado__in=['Agendada', 'Facturada'],
                factura__isnull=True
            ).order_by('fecha', 'hora').first()
            or
            Cita.objects.filter(
                paciente=paciente,
                fecha__gte=date.today(),
                estado__in=['Agendada', 'Facturada'],
            ).order_by('fecha', 'hora').first()
            )

        except Paciente.DoesNotExist:
            paciente = None
            cita = None

    context = {
        'paciente': paciente,
        'cita': cita,
    }
    return render(request, 'pacientes/buscar_paciente.html', context)


# Crear paciente
def crear_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pacientes:buscar_paciente')
    else:
        form = PacienteForm()
    return render(request, 'pacientes/form_paciente.html', {
        'form': form,
        'titulo': 'Crear Paciente',
    })

# Editar paciente
def editar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('pacientes:buscar_paciente')
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'pacientes/form_paciente.html', {
        'form': form,
        'titulo': 'Editar Paciente',
    })

# Eliminar paciente
def eliminar_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        paciente.delete()
        return redirect('pacientes:buscar_paciente')
    return render(request, 'pacientes/confirmar_eliminacion.html', {
        'paciente': paciente
    })

# Ver detalle de paciente
def detalle_paciente(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    return render(request, 'pacientes/detalle_paciente.html', {
        'paciente': paciente
    })

def cargar_municipios(request):
    departamento_id = request.GET.get('departamento')
    municipios = Municipio.objects.filter(departamento_id=departamento_id).order_by('nombre')
    municipios_data = [{'id': m.id, 'nombre': m.nombre} for m in municipios]
    return JsonResponse(municipios_data, safe=False)

@require_POST
def admitir_paciente(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)

    # Cambiar estado de la cita
    cita.estado = 'Admitida'
    cita.save()

    # Redireccionar a buscar paciente para mostrar que ya fue admitido
    messages.success(request, f'Cita del paciente {cita.paciente} admitida correctamente.')
    return redirect('pacientes:buscar_paciente')