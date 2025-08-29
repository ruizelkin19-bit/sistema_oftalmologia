from django.shortcuts import render, get_object_or_404, redirect
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.dateparse import parse_date

from citas.models import Cita
from .models import Factura, FacturaDetalle
from .forms import FacturaForm

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, inch
from decimal import Decimal
from num2words import num2words
from django.conf import settings
from django.views.decorators.clickjacking import xframe_options_exempt


def listado_facturas(request):
    documento = request.GET.get('documento', '').strip()
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    facturas = Factura.objects.select_related('paciente').order_by('-fecha')

    if documento:
        facturas = facturas.filter(paciente__numDocumentoIdentificacion__icontains=documento)

    if fecha_inicio:
        fi = parse_date(fecha_inicio)
        if fi:
            facturas = facturas.filter(fecha__date__gte=fi)
    if fecha_fin:
        ff = parse_date(fecha_fin)
        if ff:
            facturas = facturas.filter(fecha__date__lte=ff)

    paginator = Paginator(facturas, 10)
    page_number = request.GET.get('page')
    facturas_page = paginator.get_page(page_number)

    return render(request, 'facturacion/listado_facturas.html', {
        'facturas': facturas_page,
        'documento': documento,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    })

@xframe_options_exempt
def generar_factura_pdf(request, factura_id):
    from decimal import Decimal
    from num2words import num2words
    from django.http import HttpResponse
    from django.shortcuts import get_object_or_404
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from django.conf import settings

    factura = get_object_or_404(Factura, id=factura_id)
    cita = factura.cita
    paciente = factura.paciente
    cups = getattr(cita, 'codigo_cups', None)

    # --- Usar los valores exactos guardados ---
    subtotal = factura.subtotal or Decimal("0.00")
    descuento = factura.descuento or Decimal("0.00")
    iva = factura.impuestos or Decimal("0.00")
    copago = factura.copago or Decimal("0.00")
    cuota_moderadora = factura.cuota_moderadora or Decimal("0.00")
    bonos = factura.bonos or Decimal("0.00")
    total = factura.total or Decimal("0.00")
    total_letras = (num2words(total, lang='es') + " MONEDA LEGAL").upper() if total > 0 else ""

    # PDF Carta Vertical
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=factura_{factura.numero_factura}.pdf'
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter  # Tamaño carta vertical

    # --- Datos IPS ---
    ips = settings.IPS_CONFIG
    p.setFont("Helvetica-Bold", 11)
    p.drawString(40, height - 30, ips["nombre"])
    p.setFont("Helvetica", 9)
    p.drawString(40, height - 50, f"NIT : {ips['nit']}")
    p.drawString(40, height - 65, f"DIRECCIÓN : {ips['direccion']}")
    p.drawString(40, height - 80, f"TEL : {ips['telefono']}  EMAIL: {ips['email']}")

    # Número factura y fecha
    p.setFont("Helvetica-Bold", 9)
    p.drawRightString(width - 40, height - 30, f"FACTURA DE VENTA No: GC {factura.numero_factura}")
    p.setFont("Helvetica", 8)
    p.drawRightString(width - 40, height - 50, f"FECHA : {factura.fecha.strftime('%Y.%m.%d')}")
    p.drawRightString(width - 40, height - 65, f"N° CONTROL: {factura.numero_control}")

    # Datos del cliente
    y = height - 100
    p.setFont("Helvetica-Bold", 8)
    p.drawString(40, y, "CLIENTE :")
    p.setFont("Helvetica", 8)
    p.drawString(95, y, paciente.nombre)

    p.setFont("Helvetica-Bold", 8)
    p.drawString(350, y, "TELÉFONO :")
    p.setFont("Helvetica", 8)
    p.drawString(420, y, getattr(paciente, 'telefono', ''))

    y -= 14
    p.setFont("Helvetica-Bold", 8)
    p.drawString(40, y, "DIRECCIÓN :")
    p.setFont("Helvetica", 8)
    p.drawString(95, y, getattr(paciente, 'direccion', ''))

    # Separador
    y -= 10
    p.line(40, y, width - 40, y)
    y -= 18

    # Cabecera tabla
    p.setFont("Helvetica-Bold", 8)
    p.drawString(40, y, "CÓDIGO")
    p.drawString(100, y, "PRODUCTO / SERVICIO")
    p.drawString(320, y, "CANT")
    p.drawString(370, y, "V. UNIT")
    p.drawString(430, y, "DESC")
    if factura.iva_aplica:
        p.drawString(480, y, "IVA")
    p.drawString(530, y, "TOTAL")

    y -= 8
    p.line(40, y, width - 40, y)
    y -= 12
    p.setFont("Helvetica", 8)

    # --- Fila de servicio ---
    if cups:
        p.drawString(40, y, str(cups.codigo_cups))
        p.drawString(100, y, cups.nombre[:35])
        p.drawRightString(360, y, "1")
        p.drawRightString(410, y, f"{subtotal:,.2f}")
        p.drawRightString(460, y, f"{descuento:,.2f}")
        if factura.iva_aplica:
            p.drawRightString(510, y, f"{iva:,.2f}")
        p.drawRightString(570, y, f"{total:,.2f}")  # 🔹 total exacto
        y -= 14

    # --- Totales ---
    firma_y = 70
    y_tot = 230

    p.setFont("Helvetica-Bold", 8)
    p.drawRightString(520, y_tot, "SUBTOTAL :")
    p.drawRightString(570, y_tot, f"{subtotal:,.2f}")
    y_tot -= 14
    p.drawRightString(520, y_tot, "DESCUENTO :")
    p.drawRightString(570, y_tot, f"{descuento:,.2f}")
    if factura.iva_aplica:
        y_tot -= 14
        p.drawRightString(520, y_tot, "IVA :")
        p.drawRightString(570, y_tot, f"{iva:,.2f}")

    if copago:
        y_tot -= 14
        p.drawRightString(520, y_tot, "COPAGO :")
        p.drawRightString(570, y_tot, f"{copago:,.2f}")
    if cuota_moderadora:
        y_tot -= 14
        p.drawRightString(520, y_tot, "CUOTA MODERADORA :")
        p.drawRightString(570, y_tot, f"{cuota_moderadora:,.2f}")
    if bonos:
        y_tot -= 14
        p.drawRightString(520, y_tot, "BONOS :")
        p.drawRightString(570, y_tot, f"{bonos:,.2f}")

    y_tot -= 14
    p.drawRightString(520, y_tot, "TOTAL :")
    p.drawRightString(570, y_tot, f"{total:,.2f}")

    # Forma de pago y total en letras
    y_forma_pago = firma_y + 85
    p.setFont("Helvetica", 8)
    p.drawString(50, y_forma_pago, f"FORMA DE PAGO : {factura.get_forma_pago_display()}")
    y_forma_pago -= 14
    p.drawString(50, y_forma_pago, f"SON : {total_letras}")

    # Recuadro firmas
    p.rect(50, firma_y, 220, 40)
    p.drawCentredString(160, firma_y + 10, "FIRMA Y SELLO DE EMISIÓN")
    p.rect(300, firma_y, 220, 40)
    p.drawCentredString(410, firma_y + 10, "FIRMA Y SELLO DE RECIBIDO")

    # Pie de página
    p.setFont("Helvetica", 6)
    p.drawString(40, 40, f"AUTORIZACIÓN DIAN {factura.numero_control}  FECHA: {factura.fecha.strftime('%Y.%m.%d')}  DEL NÚMERO: GC{factura.numero_factura} AL: {factura.numero_factura}")
    p.drawString(40, 28, "IVA RÉGIMEN COMÚN NO CAUSA - NO SOMOS AUTORRETENEDORES NI SOMOS GRANDES CONTRIBUYENTES")
    p.drawString(40, 16, "AUTOMIPRESOR: CALLE 93 No. 15-51 OF. 206 TEL: 6185299 - BOGOTÁ D.C. - COLOMBIA")

    p.showPage()
    p.save()
    return response


def facturar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    paciente = cita.paciente
    tarifa = getattr(cita, 'codigo_cups', None)

    # Verificar si ya existe factura
    if hasattr(cita, 'factura'):
        return render(request, 'facturacion/factura_ya_existente.html', {
            'factura': cita.factura,
            'cita': cita,
            'paciente': paciente
        })

    if request.method == 'POST':
        form_factura = FacturaForm(request.POST)
        if form_factura.is_valid():
            factura = form_factura.save(commit=False)
            factura.cita = cita
            factura.paciente = paciente

            # 🔹 Asignar los valores calculados directamente al modelo
            factura.subtotal = form_factura.cleaned_data['subtotal']
            factura.descuento = form_factura.cleaned_data['descuento']
            factura.impuestos = form_factura.cleaned_data['impuestos']
            factura.total = form_factura.cleaned_data['total']
            factura.copago = form_factura.cleaned_data['copago']
            factura.cuota_moderadora = form_factura.cleaned_data['cuota_moderadora']
            factura.bonos = form_factura.cleaned_data['bonos']
            factura.iva_aplica = form_factura.cleaned_data['iva_aplica']
            factura.valor_letras = form_factura.cleaned_data['valor_letras']
            factura.observaciones = form_factura.cleaned_data.get('observaciones', '')

            factura.save()

            # 🔹 Crear detalle de la factura con los valores exactos
            if tarifa:
                FacturaDetalle.objects.create(
                    factura=factura,
                    codigo=getattr(tarifa, 'codigo_cups', 'CONS'),
                    producto=f"Consulta oftalmológica - {cita.fecha.strftime('%d/%m/%Y')}",
                    cantidad=1,
                    valor_unitario=factura.subtotal,
                    descuento=factura.descuento,
                    iva=factura.impuestos,
                    total=factura.total  # 🔹 incluir total exacto en detalle
                )

            # Cambiar estado de la cita
            cita.estado = 'Facturada'
            cita.save()

            messages.success(request, '✅ Factura creada correctamente.')
            return redirect('facturacion:detalle_factura', factura_id=factura.id)
        else:
            messages.error(request, f"❌ Hay errores de validación: {form_factura.errors}")
    else:
        # Inicializar formulario con subtotal si hay tarifa
        initial = {}
        if tarifa:
            initial['subtotal'] = getattr(tarifa, 'valor', 0)
        form_factura = FacturaForm(initial=initial)

    return render(request, 'facturacion/facturar_cita.html', {
        'form_factura': form_factura,
        'cita': cita,
        'paciente': paciente,
        'tarifa': tarifa,
        'desde_busqueda': False
    })

def detalle_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    return render(request, 'facturacion/detalle_factura.html', {'factura': factura})

def buscar_cita(request):
    q = (request.GET.get('q') or '').strip()
    fecha_str = (request.GET.get('fecha') or '').strip()

    citas = (Cita.objects
             .select_related('paciente', 'codigo_cups')
             .filter(estado='Agendada', factura__isnull=True))

    if q:
        citas = citas.filter(
            Q(paciente__numDocumentoIdentificacion__icontains=q) |
            Q(paciente__nombre__icontains=q)
        )

    if fecha_str:
        fecha = parse_date(fecha_str)
        if fecha:
            citas = citas.filter(fecha=fecha)

    citas = citas.order_by('fecha', 'hora')

    paginator = Paginator(citas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'facturacion/buscar_cita.html', {
        'citas': page_obj,
        'q': q,
        'fecha': fecha_str,
    })
