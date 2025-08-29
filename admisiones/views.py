from django.shortcuts import render, redirect, get_object_or_404
from .models import Admision
from .forms import AdmisionForm
from historias.models import HistoriaClinica
from django.utils.timezone import localdate
from django.contrib import messages
from citas.models import Cita
from django.utils import timezone

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, inch
from num2words import num2words

from django.views.decorators.clickjacking import xframe_options_exempt


@xframe_options_exempt
def generar_admision_pdf(request, admision_id):
    """
    Genera un PDF con la información de la admisión según el modelo Admision.
    Formato media carta horizontal.
    """
    admision = get_object_or_404(Admision, id=admision_id)
    paciente = admision.paciente
    cita = admision.cita

    # Media carta horizontal
    half_letter = (5.5 * inch, 8.5 * inch)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=admision_{admision.numero_control}.pdf'
    p = canvas.Canvas(response, pagesize=landscape(half_letter))
    width, height = landscape(half_letter)

    # --- Encabezado ---
    p.setFont("Helvetica-Bold", 11)
    p.drawString(40, height - 30, "HOSPITAL / CONSULTORIO XYZ")
    p.setFont("Helvetica", 9)
    p.drawString(40, height - 45, "NIT: 123456789-0")

    p.setFont("Helvetica-Bold", 9)
    p.drawRightString(550, height - 30, f"ADMISIÓN No: {admision.numero_control}")
    p.setFont("Helvetica", 8)
    p.drawRightString(550, height - 45, f"FECHA: {admision.fecha_admision.strftime('%Y-%m-%d')}")
    p.drawRightString(550, height - 58, f"ESTADO: {admision.estado.capitalize()}")

    # --- Datos del paciente ---
    y = height - 80
    p.setFont("Helvetica-Bold", 8)
    p.drawString(40, y, "PACIENTE:")
    p.setFont("Helvetica", 8)
    p.drawString(95, y, f"{paciente.nombre}")

    p.setFont("Helvetica-Bold", 8)
    p.drawString(350, y, "DOCUMENTO:")
    p.setFont("Helvetica", 8)
    p.drawString(420, y, paciente.numDocumentoIdentificacion)

    y -= 14
    p.setFont("Helvetica-Bold", 8)
    p.drawString(40, y, "TELÉFONO:")
    p.setFont("Helvetica", 8)
    p.drawString(95, y, getattr(paciente, 'telefono', 'N/A'))

    y -= 14
    p.setFont("Helvetica-Bold", 8)
    p.drawString(40, y, "DIRECCIÓN:")
    p.setFont("Helvetica", 8)
    p.drawString(95, y, getattr(paciente, 'direccion', 'N/A'))

    y -= 14
    p.setFont("Helvetica-Bold", 8)
    p.drawString(40, y, "CITA:")
    p.setFont("Helvetica", 8)
    cita_texto = f"{cita.fecha} {cita.hora.strftime('%H:%M')} - {cita.codigo_cups.nombre}" if cita else "Sin cita"
    p.drawString(95, y, cita_texto)

    y -= 10
    p.line(40, y, 570, y)
    y -= 18

    # --- Detalles de admisión ---
    p.setFont("Helvetica-Bold", 8)
    p.drawString(40, y, "TIPO DE USUARIO:")
    p.setFont("Helvetica", 8)
    p.drawString(130, y, paciente.get_tipoUsuario_display() or "N/A")

    y -= 14
    p.setFont("Helvetica-Bold", 8)
    p.drawString(40, y, "RÉGIMEN:")
    p.setFont("Helvetica", 8)
    p.drawString(130, y, paciente.get_regimen_display() or "N/A")

    y -= 14
    p.setFont("Helvetica-Bold", 8)
    p.drawString(40, y, "ENTIDAD RESPONSABLE:")
    p.setFont("Helvetica", 8)
    p.drawString(160, y, admision.entidad_responsable or "N/A")

    y -= 14
    p.setFont("Helvetica-Bold", 8)
    p.drawString(40, y, "N° AUTORIZACIÓN:")
    p.setFont("Helvetica", 8)
    p.drawString(140, y, admision.numero_autorizacion or "N/A")

    y -= 14
    p.setFont("Helvetica-Bold", 8)
    p.drawString(40, y, "MOTIVO DE CONSULTA:")
    p.setFont("Helvetica", 8)
    y -= 12
    p.drawString(40, y, admision.motivo_consulta or "N/A")

    y -= 14
    p.setFont("Helvetica-Bold", 8)
    p.drawString(40, y, "DIAGNÓSTICO PRESUNTIVO:")
    p.setFont("Helvetica", 8)
    p.drawString(160, y, admision.diagnostico_presuntivo or "N/A")

    y -= 14
    p.setFont("Helvetica-Bold", 8)
    p.drawString(40, y, "OBSERVACIONES:")
    p.setFont("Helvetica", 8)
    y -= 12
    p.drawString(40, y, admision.observaciones or "N/A")

    # --- Recuadro de firmas ---
    firma_y = 70
    p.rect(50, firma_y, 220, 40)
    p.drawCentredString(160, firma_y + 10, "FIRMA Y SELLO DE RECEPCIÓN")
    p.rect(300, firma_y, 220, 40)
    p.drawCentredString(410, firma_y + 10, "FIRMA Y SELLO DEL RESPONSABLE")

    # Pie de página
    p.setFont("Helvetica", 6)
    p.drawString(40, 40, f"ADMISIÓN: {admision.numero_control}  FECHA: {admision.fecha_admision.strftime('%Y-%m-%d')}")
    p.drawString(40, 28, "DOCUMENTO GENERADO AUTOMÁTICAMENTE")

    # Guardar PDF
    p.showPage()
    p.save()
    return response


def crear_admision(request):
    cita_id = request.GET.get('cita_id')  # Obtener el ID de la cita desde la URL
    cita = None
    if cita_id:
        cita = get_object_or_404(Cita, id=cita_id)  # Obtener la cita con el ID

    # Verificar si ya existe una admisión asociada a la cita
    if cita and Admision.objects.filter(cita=cita).exists():
        admision_existente = Admision.objects.get(cita=cita)
        messages.info(request, "ℹ️ Esta cita ya tiene una admisión registrada.")
        return redirect('admisiones:ver_admision', admision_id=admision_existente.id)

    if request.method == 'POST':
        form = AdmisionForm(request.POST, cita=cita)
        if form.is_valid():
            admision = form.save(commit=False)
            admision.cita = cita  # Asociar la cita (id válido)
            admision.estado = 'Admitido'
            admision.paciente = cita.paciente  # Asociar el paciente correcto
            admision.save()

            # Actualizar estado de la cita
            if cita:
                cita.estado = 'Admitida'
                cita.save()

            # Crear historia clínica si no existe
            historia_existente = HistoriaClinica.objects.filter(cita=cita).first()
            if not historia_existente:
                historia = HistoriaClinica.objects.create(
                    paciente=admision.paciente,
                    cita=cita,
                    admision=admision,
                    fecha=localdate(),
                )
                messages.success(request, "✅ Historia clínica creada automáticamente.")
                return redirect('historias:detalle_historia', pk=historia.id)
            else:
                messages.info(request, "ℹ️ Ya existe una historia clínica para esta admisión.")
                return redirect('historias:detalle_historia', pk=historia_existente.id)
    else:
        # Inicialización para el formulario
        initial_data = {}
        if cita:
            initial_data = {
                'cita': cita.id,  # id oculto (hidden field)
                'cita_display': cita.codigo_cups.nombre,  # 👈 mostrar el nombre del procedimiento
                'paciente': cita.paciente.id,
            }
        form = AdmisionForm(initial=initial_data, cita=cita)

    return render(request, 'admisiones/crear_admision.html', {'form': form, 'cita': cita})



def ver_admision(request, admision_id):
    admision = get_object_or_404(Admision, id=admision_id)
    return render(request, 'admisiones/detalle_admision.html', {'admision': admision})


def listado_admisiones(request):
    documento = request.GET.get("documento", "").strip()
    fecha_inicio = request.GET.get("fecha_inicio", "")
    fecha_fin = request.GET.get("fecha_fin", "")
    estado = request.GET.get("estado", "")

    admisiones = Admision.objects.select_related('paciente', 'cita').order_by(
        'paciente__numDocumentoIdentificacion', '-fecha_admision'
    )

    # 📌 Filtro por defecto: solo hoy y estado "Admitido"
    if not fecha_inicio and not fecha_fin and not documento:
        admisiones = admisiones.filter(fecha_admision__date=localdate(), estado="Admitido")

    if documento:
        admisiones = admisiones.filter(
            paciente__numDocumentoIdentificacion__iexact=documento
        )
    if fecha_inicio:
        admisiones = admisiones.filter(fecha_admision__date__gte=fecha_inicio)
    if fecha_fin:
        admisiones = admisiones.filter(fecha_admision__date__lte=fecha_fin)
    if estado:
        admisiones = admisiones.filter(estado=estado)

    context = {
        "admisiones": admisiones,
        "documento": documento,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "estado": estado,
        "fecha": localdate(),
    }
    return render(request, "admisiones/listado_admisiones.html", context)


def marcar_atendido(request, admision_id):
    admision = get_object_or_404(Admision, id=admision_id)
    admision.estado = 'atendido'
    admision.save()
    messages.success(request, f"✅ Paciente {admision.paciente.nombre} marcado como atendido.")
    return redirect('listado_admisiones')
