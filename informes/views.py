from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
import datetime
import openpyxl
from historias.models import HistoriaClinica
from facturacion.models import Factura
from admisiones.models import Admision
from pacientes.models import Paciente
from citas.models import Cita

def listado_informes(request):
    # Renderiza la página con el formulario para filtrar y elegir módulo
    return render(request, 'informes/listado_informes.html')


def exportar_excel(request, modulo):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # Validar fechas
    if not fecha_inicio or not fecha_fin:
        return HttpResponse("Debe enviar fecha_inicio y fecha_fin", status=400)

    fecha_inicio = datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    fecha_fin = datetime.datetime.strptime(fecha_fin, '%Y-%m-%d').date()

    # Preparar respuesta y libro Excel
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    filename = f"{modulo}_{fecha_inicio}_a_{fecha_fin}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = modulo.capitalize()

    if modulo == 'pacientes':
        pacientes = Paciente.objects.filter(fecha_creacion__range=(fecha_inicio, fecha_fin))
        ws.append(['ID', 'Nombre', 'Documento', 'Fecha Creación'])
        for p in pacientes:
            ws.append([p.id, p.nombre, p.numDocumentoIdentificacion, p.fecha_creacion])

    elif modulo == 'citas':
        citas = Cita.objects.filter(fecha__range=(fecha_inicio, fecha_fin))
        ws.append(['ID', 'Paciente', 'Fecha', 'Estado'])
        for c in citas:
            ws.append([c.id, c.paciente.nombre, c.fecha, c.estado])

    elif modulo == 'historias':
        historias = HistoriaClinica.objects.filter(fecha__range=(fecha_inicio, fecha_fin))
        ws.append(['ID', 'Paciente', 'Número Control', 'Fecha'])
        for h in historias:
            ws.append([h.id, h.paciente.nombre, h.numero_control, h.fecha])

    elif modulo == 'productos':
        # Si tienes modelo Productos, poner aquí el filtro y campos
        ws.append(['ID', 'Nombre Producto', 'Cantidad', 'Precio'])
        # productos = Producto.objects.filter(fecha_creacion__range=(fecha_inicio, fecha_fin))
        # for prod in productos:
        #     ws.append([prod.id, prod.nombre, prod.cantidad, prod.precio])
        ws.append(['Función no implementada aún'])
    else:
        return HttpResponse("Módulo no soportado", status=400)

    wb.save(response)
    return response


def informe_traza(request, numero_control):
    # Buscar la factura con el número de control recibido
    try:
        factura = Factura.objects.get(numero_control=numero_control)
    except Factura.DoesNotExist:
        messages.error(request, "Número de control no encontrado en facturación.")
        return redirect('informes:listado_informes')

    cita = factura.cita  # Obtenemos la cita relacionada a la factura

    try:
        admision = Admision.objects.get(cita=cita)
    except Admision.DoesNotExist:
        admision = None  # Puede que no exista admisión todavía

    historia = HistoriaClinica.objects.filter(cita=cita).first()

    context = {
        "factura": factura,
        "cita": cita,
        "admision": admision,
        "historia": historia,
    }

    return render(request, 'informes/informe_traza.html', context)