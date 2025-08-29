from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime, date, timedelta, time
from .models import Cita
from .forms import CitaForm
from pacientes.models import Paciente
from django.contrib import messages
import calendar
from calendar import monthrange
from historias.models import HistoriaClinica  # Ajusta si está en otra app
from django.utils.timezone import localdate  # asegúrate de tener esto
from django.utils.timezone import localdate, localtime



def listado_citas(request):
    documento = request.GET.get("documento", "").strip()
    fecha_inicio = request.GET.get("fecha_inicio", "")
    fecha_fin = request.GET.get("fecha_fin", "")
    estado_cita = request.GET.get("estado", "")

    citas = Cita.objects.select_related('paciente').order_by(
        'paciente__numDocumentoIdentificacion', '-fecha'
    )

    # 📌 Solo aplica el filtro por defecto si NO hay fechas NI documento
    if not fecha_inicio and not fecha_fin and not documento:
        citas = citas.filter(fecha=localdate(), estado="Agendada")

    if documento:
        citas = citas.filter(
            paciente__numDocumentoIdentificacion__iexact=documento
        )
    if fecha_inicio:
        citas = citas.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        citas = citas.filter(fecha__lte=fecha_fin)
    if estado_cita:
        citas = citas.filter(estado=estado_cita)

    context = {
        "citas": citas,
        "documento": documento,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "estado_cita": estado_cita,
        "titulo": "Listado de Citas"
    }
    return render(request, "citas/listado_citas.html", context)

def crear_cita(request):
    fecha = request.GET.get('fecha')
    hora = request.GET.get('hora')
    documento = request.GET.get('documento')

    paciente = None
    if documento:
        paciente = Paciente.objects.filter(numDocumentoIdentificacion=documento).first()

    if request.method == 'POST':
        documento = request.POST.get('documento')
        paciente = Paciente.objects.filter(numDocumentoIdentificacion=documento).first()
        form = CitaForm(request.POST)
        if form.is_valid():
            if paciente:
                cita = form.save(commit=False)
                cita.paciente = paciente
                cita.save()
                messages.success(request, 'Cita agendada con éxito.')
                return redirect('citas:listado_citas')
            else:
                messages.error(request, 'No se encontró un paciente con ese documento.')
    else:
        form = CitaForm(initial={
            'fecha': fecha,
            'hora': hora
        })

    return render(request, 'citas/form_cita.html', {
        'form': form,
        'fecha': fecha,
        'hora': hora,
        'documento': documento,
        'paciente': paciente
    })


def agenda_mes(request):
    hoy = date.today()
    mes = int(request.GET.get('mes', hoy.month))
    anio = int(request.GET.get('anio', hoy.year))

    cal = calendar.Calendar(firstweekday=0)
    semanas = cal.monthdatescalendar(anio, mes)

    citas_mes = Cita.objects.filter(fecha__year=anio, fecha__month=mes, estado='Agendada')

    dias_con_citas = {}
    for cita in citas_mes:
        key = cita.fecha.strftime('%Y-%m-%d')
        dias_con_citas[key] = dias_con_citas.get(key, 0) + 1

    contexto = {
        'calendario': semanas,
        'mes_actual': date(anio, mes, 1),
        'mes_anterior': date(anio, mes, 1) - timedelta(days=1),
        'mes_siguiente': date(anio, mes, monthrange(anio, mes)[1]) + timedelta(days=1),
        'dias_con_citas': dias_con_citas,
    }
    return render(request, 'citas/agenda_mes.html', contexto)


def agenda_dia(request, anio, mes, dia):
    fecha = datetime(int(anio), int(mes), int(dia)).date()

    hora_inicio = time(8, 0)
    hora_fin = time(17, 0)
    intervalo = timedelta(minutes=30)

    horas_disponibles = []
    hora_actual = datetime.combine(fecha, hora_inicio)
    fin = datetime.combine(fecha, hora_fin)
    while hora_actual <= fin:
        horas_disponibles.append(hora_actual.time())
        hora_actual += intervalo

    # Quitar horas ya ocupadas
    horas_ocupadas = Cita.objects.filter(
        fecha=fecha,
        estado='Agendada'
    ).values_list('hora', flat=True)
    horas_disponibles = [h for h in horas_disponibles if h not in horas_ocupadas]

    # 🔒 Filtrar por hora actual si es hoy
    hoy = localdate()
    ahora = localtime().time()
    if fecha == hoy:
        horas_disponibles = [h for h in horas_disponibles if h > ahora]

    context = {
        'fecha': fecha,
        'horas_disponibles': horas_disponibles,
    }
    return render(request, 'citas/agenda_dia.html', context)

def agenda_disponible(request):
    hoy = localdate()  # 👈 esto es lo que faltaba
    mes = int(request.GET.get('mes', hoy.month))
    anio = int(request.GET.get('anio', hoy.year))

    cal = calendar.Calendar(firstweekday=6)
    semanas = cal.monthdatescalendar(anio, mes)

    citas_mes = Cita.objects.filter(fecha__year=anio, fecha__month=mes, estado='Agendada')
    dias_con_citas = {cita.fecha for cita in citas_mes}

    meses = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre'),
    ]

    años = list(range(2024, 2031))

    context = {
        'mes': mes,
        'anio': anio,
        'semanas': semanas,
        'dias_con_citas': dias_con_citas,
        'meses': meses,
        'años': años,
        'hoy': hoy,  # ✅ necesario para la plantilla
    }
    return render(request, 'citas/agenda_disponible.html', context)


def agenda_semanal(request):
    hoy = datetime.today().date()
    start_date_str = request.GET.get('start_date')
    if start_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    else:
        start_date = hoy - timedelta(days=hoy.weekday())

    end_date = start_date + timedelta(days=6)
    horarios = [time(hour=h) for h in range(8, 18)]
    citas = Cita.objects.filter(fecha__range=(start_date, end_date))

    agenda = []
    for hora in horarios:
        fila = {'hora': hora, 'dias': []}
        for i in range(7):
            dia = start_date + timedelta(days=i)
            cita = citas.filter(fecha=dia, hora=hora).first()
            fila['dias'].append({'fecha': dia, 'cita': cita})
        agenda.append(fila)

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'agenda': agenda,
    }
    return render(request, 'citas/agenda_semanal.html', context)


def agenda_calendario(request):
    hoy = date.today()
    mes = int(request.GET.get('mes', hoy.month))
    anio = int(request.GET.get('anio', hoy.year))

    cal = calendar.Calendar(firstweekday=6)
    semanas = cal.monthdatescalendar(anio, mes)

    citas_mes = Cita.objects.filter(fecha__year=anio, fecha__month=mes)
    dias_con_citas = {cita.fecha for cita in citas_mes}

    meses = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre'),
    ]

    contexto = {
        'mes': mes,
        'anio': anio,
        'semanas': semanas,
        'dias_con_citas': dias_con_citas,
        'meses': meses,
    }
    return render(request, 'citas/agenda_calendario.html', contexto)

def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)

    # Validación: solo se pueden editar citas en estado "Agendada"
    if cita.estado != 'Agendada':
        messages.warning(request, 'Solo se pueden editar las citas que están agendadas.')
        return redirect('citas:listado_citas')

    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, 'La cita ha sido actualizada correctamente.')
            return redirect('citas:listado_citas')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = CitaForm(instance=cita)

    return render(request, 'citas/editar_cita.html', {'form': form, 'cita': cita})

def cancelar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)

    if cita.estado == 'Cancelada':
        messages.info(request, 'La cita ya está cancelada.')
    elif cita.estado != 'Agendada':
        messages.warning(request, 'No se puede cancelar una cita que ya fue admitida o finalizada.')
    else:
        cita.estado = 'Cancelada'
        cita.save()
        messages.success(request, 'La cita ha sido cancelada exitosamente.')

    return redirect('citas:listado_citas')

def admitir_paciente(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)

    if cita.estado != 'Agendada':
        messages.warning(request, 'Esta cita ya fue admitida, atendida o cancelada.')
        return redirect('citas:listado_citas')

    # Validar que no tenga historia ya creada
    historia_existente = HistoriaClinica.objects.filter(cita=cita).first()
    if historia_existente:
        messages.info(request, 'Ya existe historia clínica para esta cita.')
        return redirect('historias:ver_historia', pk=historia_existente.pk)

    # Actualizar estado
    cita.estado = 'Admitida'
    cita.save()

    # Crear historia clínica
    historia = HistoriaClinica.objects.create(
        paciente=cita.paciente,
        cita=cita,
        observaciones='',
        diagnostico='',
    )

    messages.success(request, 'Paciente admitido y historia creada.')
    return redirect('historias:ver_historia', pk=historia.pk)
