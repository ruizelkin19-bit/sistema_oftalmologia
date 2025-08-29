from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from facturacion.models import Factura
from pacientes.models import Paciente
import json
from django.core.paginator import Paginator


def listado_rips(request):
    # Filtros opcionales (puedes agregar más si quieres)
    documento = request.GET.get("documento", "").strip()
    fecha_inicio = request.GET.get("fecha_inicio", "")
    fecha_fin = request.GET.get("fecha_fin", "")

    facturas = Factura.objects.select_related('paciente').order_by('-fecha')

    if documento:
        facturas = facturas.filter(paciente__numDocumentoIdentificacion__iexact=documento)
    if fecha_inicio:
        facturas = facturas.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        facturas = facturas.filter(fecha__lte=fecha_fin)

    paginator = Paginator(facturas, 10)  # 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "facturas": page_obj,
        "documento": documento,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    }
    return render(request, "rips/listado_rips.html", context)


def exportar_us(request):
    factura_id = request.GET.get('factura_id')

    if factura_id:
        # Obtener la factura y paciente asociado
        factura = get_object_or_404(Factura, id=factura_id)
        paciente = factura.paciente
        pacientes = [paciente]
    else:
        # Si no hay factura_id, exportar todos los pacientes
        pacientes = Paciente.objects.all()

    datos = []

    for p in pacientes:
        datos.append({
            "tipo_identificacion": p.tipoDocumentoIdentificacion or "CC",
            "numero_identificacion": p.numDocumentoIdentificacion or "",
            "primer_apellido": p.primer_apellido or "",
            "primer_nombre": p.primer_nombre or "",
            "fecha_nacimiento": p.fechaNacimiento.strftime('%Y-%m-%d') if p.fechaNacimiento else "",
            "sexo": p.codSexo or "O",
            "codigo_departamento": p.departamentoResidencia.codigo if p.departamentoResidencia else "",
            "codigo_municipio": p.codMunicipioResidencia.codigo_dane if p.codMunicipioResidencia else "",
            "zona_residencial": p.codZonaTerritorialResidencia or "U",
        })

    # Crear respuesta JSON para descarga
    response = HttpResponse(
        json.dumps(datos, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    if factura_id:
        filename = f"US_factura_{factura_id}.json"
    else:
        filename = "US_todos_pacientes.json"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response
