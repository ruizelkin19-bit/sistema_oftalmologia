from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from django.http import Http404
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from admisiones.models import Admision
from django.utils.timezone import localdate
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import HistoriaClinica
from .forms import HistoriaClinicaForm
from citas.models import Cita
from pacientes.models import Paciente
from reportlab.lib import colors 
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape, inch

from django.views.decorators.clickjacking import xframe_options_exempt

def safe_text(valor):
    """Convierte None a cadena vacía para evitar errores"""
    return str(valor) if valor else "N/A"


def generar_historia_pdf(request, historia_id):
    historia = get_object_or_404(HistoriaClinica, id=historia_id)

    # Respuesta HTTP
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="historia_clinica.pdf"'

    # Documento
    doc = SimpleDocTemplate(response, pagesize=letter,
                            rightMargin=30, leftMargin=30,
                            topMargin=20, bottomMargin=20)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Titulo", fontSize=14, alignment=1, textColor=colors.HexColor("#000000"), spaceAfter=12))
    styles.add(ParagraphStyle(name="Seccion", fontSize=11, textColor=colors.HexColor("#154360"), spaceBefore=10, spaceAfter=6, underlineWidth=1))
    styles.add(ParagraphStyle(name="NormalBold", fontSize=9, leading=12, textColor=colors.black))

    story = []

    # ================= ENCABEZADO =================
    story.append(Paragraph("HISTORIA CLÍNICA OFTALMOLÓGICA", styles["Titulo"]))
    story.append(Spacer(1, 6))

    # ================= DATOS DE IDENTIFICACIÓN =================
    ficha = [
        ["Número de Control:", safe_text(historia.numero_control), "Fecha:", safe_text(historia.fecha.strftime("%d/%m/%Y"))],
        ["Paciente:", safe_text(historia.paciente), "Teléfono:", safe_text(historia.telefono)],
        ["Dirección:", safe_text(historia.direccion), "Ocupación:", safe_text(historia.ocupacion)],
    ]
    tabla_ficha = Table(ficha, colWidths=[100, 180, 80, 180])
    tabla_ficha.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
    ]))
    story.append(Paragraph("DATOS DE IDENTIFICACIÓN", styles["Seccion"]))
    story.append(tabla_ficha)

    # ================= SIGNOS VITALES =================
    signos = [
        ["Tensión arterial:", safe_text(historia.tension_arterial),
         "Frecuencia cardíaca:", safe_text(historia.frecuencia_cardiaca)]
    ]
    tabla_signos = Table(signos, colWidths=[120, 150, 120, 150])
    tabla_signos.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("FONTSIZE", (0,0), (-1,-1), 9),
    ]))
    story.append(Paragraph("SIGNOS VITALES", styles["Seccion"]))
    story.append(tabla_signos)

    # ================= MOTIVO Y ANTECEDENTES =================
    antecedentes = [
        ["Motivo de Consulta", safe_text(historia.motivo_consulta)],
        ["Enfermedad Actual", safe_text(historia.enfermedad_actual)],
        ["Antecedentes Personales", safe_text(historia.antecedentes_personales)],
        ["Antecedentes Familiares", safe_text(historia.antecedentes_familiares)],
        ["Antecedentes Oftalmológicos", safe_text(historia.antecedentes_oftalmologicos)],
    ]
    tabla_ant = Table(antecedentes, colWidths=[200, 380])
    tabla_ant.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
    ]))
    story.append(Paragraph("ANTECEDENTES", styles["Seccion"]))
    story.append(tabla_ant)

    # ================= DIAGNÓSTICO Y PLAN =================
    diagnostico = [
        ["Diagnóstico Principal", safe_text(historia.diagnostico_principal)],
        ["Diagnóstico Secundario", safe_text(historia.diagnostico_secundario)],
        ["Código CIE10 Principal", safe_text(historia.cie10_principal)],
        ["Diagnósticos Adicionales", ", ".join([d.codigo for d in historia.diagnosticos_cie10.all()]) or "N/A"],
        ["Plan de Tratamiento", safe_text(historia.plan_tratamiento)],
        ["Conducta", safe_text(historia.conducta)],
        ["Observaciones", safe_text(historia.observaciones)],
    ]
    tabla_diag = Table(diagnostico, colWidths=[200, 380])
    tabla_diag.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
    ]))
    story.append(Paragraph("DIAGNÓSTICO Y PLAN", styles["Seccion"]))
    story.append(tabla_diag)

    # ================= PROFESIONAL =================
    prof = [
        ["Nombre", safe_text(historia.firmado_por)],
        ["Especialidad", safe_text(historia.especialidad)],
        ["Registro Médico", safe_text(historia.registro_medico)],
    ]
    tabla_prof = Table(prof, colWidths=[150, 430])
    tabla_prof.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("FONTSIZE", (0,0), (-1,-1), 9),
    ]))
    story.append(Paragraph("PROFESIONAL TRATANTE", styles["Seccion"]))
    story.append(tabla_prof)

    # Generar documento
    doc.build(story)
    return response

# Vista para crear una nueva historia clínica desde una cita
def crear_historia_clinica(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)

    if HistoriaClinica.objects.filter(cita=cita).exists():
        historia = HistoriaClinica.objects.get(cita=cita)
        messages.warning(request, "Ya existe una historia clínica para esta cita.")
        return redirect('historias:ver_historia_clinica', historia_id=historia.id)

    if request.method == 'POST':
        form = HistoriaClinicaForm(request.POST)
        if form.is_valid():
            historia = form.save(commit=False)
            historia.paciente = cita.paciente
            historia.cita = cita

            # Buscar admisión correspondiente
            try:
                admision = Admision.objects.get(cita=cita)
                historia.codigo_interno = admision.numero_control
                historia.admision = admision
            except Admision.DoesNotExist:
                messages.error(request, "No se encontró una admisión para esta cita.")
                return redirect('citas:listado_citas')

            historia.save()

            if cita.estado != 'Atendida':
                cita.estado = 'Atendida'
                cita.save()

            messages.success(request, "Historia clínica registrada correctamente.")
            return redirect('historias:ver_historia_clinica', historia_id=historia.id)
    else:
        form = HistoriaClinicaForm(initial={'paciente': cita.paciente.id})

    return render(request, 'historias/crear_historia_clinica.html', {
        'form': form,
        'cita': cita
    })


def listado_historias(request):
    documento = request.GET.get("documento", "").strip()
    fecha_inicio = request.GET.get("fecha_inicio", "")
    fecha_fin = request.GET.get("fecha_fin", "")
    estado_cita = request.GET.get("estado", "")

    historias = HistoriaClinica.objects.select_related('paciente', 'cita').order_by(
        'paciente__numDocumentoIdentificacion', '-cita__fecha'
    )

    # 📌 Filtro por defecto: solo hoy y estado "Admitida"
    if not fecha_inicio and not fecha_fin and not documento:
        historias = historias.filter(cita__fecha=localdate(), cita__estado="Admitida")

    if documento:
        historias = historias.filter(
            paciente__numDocumentoIdentificacion__iexact=documento
        )
    if fecha_inicio:
        historias = historias.filter(cita__fecha__gte=fecha_inicio)
    if fecha_fin:
        historias = historias.filter(cita__fecha__lte=fecha_fin)
    if estado_cita:
        historias = historias.filter(cita__estado=estado_cita)

    # 📌 Generar secuencia de documento
    secuencias = {}
    for historia in historias:
        doc = historia.paciente.numDocumentoIdentificacion
        secuencias[doc] = secuencias.get(doc, 0) + 1
        historia.doc_con_secuencia = f"{doc}-{secuencias[doc]}"

    historias = list(historias)
    historias.reverse()

    context = {
        "historias": historias,
        "documento": documento,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "estado_cita": estado_cita,
    }
    return render(request, "historias/listado_historias.html", context)


# Vista para ver detalle de historia clínica
def ver_historia_clinica(request, historia_id):
    historia = get_object_or_404(HistoriaClinica, pk=historia_id)
    paciente = historia.paciente
    nombre_completo = paciente.nombre or "Nombre no disponible"

    if request.method == 'POST':
        form = HistoriaClinicaForm(request.POST, instance=historia)
        if form.is_valid():
            form.save()

            try:
                admision = Admision.objects.get(cita=historia.cita)
                admision.estado = 'atendido'
                admision.fecha_ingreso = localdate()
                admision.save()
            except Admision.DoesNotExist:
                messages.warning(request, 'No se encontró la admisión correspondiente.')

            if historia.cita.estado != 'Atendida':
                historia.cita.estado = 'Atendida'
                historia.cita.save()

            messages.success(request, 'Historia clínica guardada y paciente marcado como atendido.')
            return redirect('historias:ver_historia_clinica', historia_id=historia.id)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = HistoriaClinicaForm(instance=historia)

    context = {
        'form': form,
        'historia': historia,
        'paciente': paciente,
        'nombre_completo': nombre_completo,
    }
    return render(request, 'historias/ver_historia_clinica.html', context)


# Ingreso desde cita (automático)
def ingresar_paciente(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    cita.estado = 'En atención'
    cita.save()

    try:
        admision = Admision.objects.get(cita=cita)
    except Admision.DoesNotExist:
        messages.error(request, 'No se encontró la admisión correspondiente.')
        return redirect('citas:listado_citas')

    historia, creada = HistoriaClinica.objects.get_or_create(
        cita=cita,
        defaults={
            'paciente': cita.paciente,
            'fecha': timezone.now(),
            'codigo_interno': admision.numero_control,
            'admision': admision,
        }
    )

    if creada:
        messages.success(request, 'Historia clínica creada correctamente.')
    else:
        messages.info(request, 'El paciente ya tenía una historia clínica creada.')

    return redirect('historias:ver_historia_clinica', historia_id=historia.id)


# Ingreso por cita (caso especial)
def dar_ingreso(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)

    try:
        admision = Admision.objects.get(cita=cita)
    except Admision.DoesNotExist:
        messages.error(request, "No se encontró la admisión correspondiente.")
        return redirect('citas:listado_citas')

    historia, creada = HistoriaClinica.objects.get_or_create(
        cita=cita,
        defaults={
            'paciente': cita.paciente,
            'fecha': datetime.now(),
            'codigo_interno': admision.numero_control,
            'admision': admision,
        }
    )

    return redirect(reverse('historias:listado_historias'))


def detalle_historia(request, pk):
    historia = get_object_or_404(HistoriaClinica, pk=pk)
    return render(request, 'historias/detalle_historia.html', {'historia': historia})


def editar_historia_clinica(request, pk):
    historia = get_object_or_404(HistoriaClinica, pk=pk)

    if request.method == 'POST':
        form = HistoriaClinicaForm(request.POST, instance=historia)
        if form.is_valid():
            form.save()
            messages.success(request, "Historia clínica actualizada exitosamente.")
            return redirect('historias:ver_historia_clinica', historia_id=historia.pk)
    else:
        form = HistoriaClinicaForm(instance=historia)

    return render(request, 'historias/editar_historia_clinica.html', {'form': form, 'historia': historia})


def atender(request, admision_id):
    admision = get_object_or_404(Admision, id=admision_id)
    cita = admision.cita
    paciente = admision.paciente

    historia, creada = HistoriaClinica.objects.get_or_create(
        admision=admision,
        defaults={
            'paciente': paciente,
            'cita': cita,
            'fecha': timezone.now(),
            'codigo_interno': admision.numero_control
        }
    )

    return redirect('historias:ver_historia_clinica', historia_id=historia.id)
