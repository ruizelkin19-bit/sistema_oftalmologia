# soportes/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Exists, OuterRef

from .models import Soporte
from .forms import SoporteForm
from facturacion.models import Factura
from admisiones.models import Admision
from historias.models import HistoriaClinica

from facturacion.views import generar_factura_pdf
from historias.views import generar_historia_pdf
from admisiones.views import generar_admision_pdf
from django.conf import settings

import os
import io
import zipfile

def eliminar_soporte(request, soporte_id):
    soporte = Soporte.objects.filter(id=soporte_id).first()
    
    if soporte:
        archivo_path = os.path.join(settings.MEDIA_ROOT, soporte.archivo.name)
        carpeta = os.path.dirname(archivo_path)  # Carpeta donde estaba el archivo

        # Eliminar archivo
        if os.path.exists(archivo_path):
            os.remove(archivo_path)

        # Eliminar soporte de la base de datos
        soporte.delete()

        # Verificar si la carpeta quedó vacía y eliminarla
        if os.path.exists(carpeta) and len(os.listdir(carpeta)) == 0:
            os.rmdir(carpeta)

        return JsonResponse({'status': 'ok', 'mensaje': 'Soporte eliminado'})
    else:
        return JsonResponse({'status': 'error', 'mensaje': 'El soporte no existe'})    

# 🔹 1️⃣ Listado de números de control
def lista_numeros_control(request):
    documento = request.GET.get("documento", "").strip()
    fecha_inicio = request.GET.get("fecha_inicio", "")
    fecha_fin = request.GET.get("fecha_fin", "")

    facturas = Factura.objects.select_related('paciente').order_by('-id')

    if documento:
        facturas = facturas.filter(paciente__numDocumentoIdentificacion__iexact=documento)
    if fecha_inicio:
        facturas = facturas.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        facturas = facturas.filter(fecha__lte=fecha_fin)

    # Creamos lista simple para el template
    numeros_control = [
        {
            "numero_control": f.numero_control,
            "numero_factura": f.numero_factura,
            "paciente": f.paciente.nombre,
            "documento": f.paciente.numDocumentoIdentificacion,
            "fecha": f.fecha,
        }
        for f in facturas
    ]

    context = {
        "numeros_control": numeros_control,
        "documento": documento,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    }
    return render(request, "soportes/lista_numeros_control.html", context)

# 🔹 2️⃣ Crear soporte ligado a NC
def cargar_soporte(request, numero_control):
    # Obtener la factura asociada al NCI
    try:
        factura = Factura.objects.get(numero_control=numero_control)
        carpeta = f"soportes/{factura.numero_factura}/"  # Carpeta dentro de MEDIA_ROOT
    except Factura.DoesNotExist:
        carpeta = "soportes/sin_factura/"

    if request.method == "POST":
        form = SoporteForm(request.POST, request.FILES)
        if form.is_valid():
            soporte = form.save(commit=False)
            soporte.numero_control = numero_control

            if soporte.archivo:
                nombre_archivo = soporte.archivo.name.split("/")[-1]  # Solo el nombre del archivo
                soporte.archivo.name = carpeta + nombre_archivo  # Concatenar solo carpeta + nombre

            soporte.save()
            messages.success(request, "Soporte creado correctamente.")
            return redirect("soportes:visor_soporte", numero_control=numero_control)
    else:
        form = SoporteForm()

    return render(request, "soportes/cargar_soporte.html", {"form": form, "numero_control": numero_control})


# 🔹 3️⃣ Visor de soportes con panel lateral
def visor_soporte(request, numero_control):
    soportes = Soporte.objects.filter(numero_control=numero_control)
    admisiones = Admision.objects.filter(numero_control=numero_control)
    historias = HistoriaClinica.objects.filter(numero_control=numero_control)
    facturas = Factura.objects.filter(numero_control=numero_control)

    # Asignar URL de PDF a cada documento
    for factura in facturas:
        factura.pdf_url = reverse('facturacion:generar_factura_pdf', args=[factura.id])
    for historia in historias:
        historia.pdf_url = reverse('historias:generar_pdf', args=[historia.id])
    for admision in admisiones:
        admision.pdf_url = reverse('admisiones:generar_pdf', args=[admision.id])

    categorias = {
        "Factura": facturas,
        "Admision": admisiones,
        "Historia Clinica": historias,
        "Soportes Adicionales": soportes,
    }

    context = {
        "numero_control": numero_control,
        "categorias": categorias,
    }
    return render(request, "soportes/visor_soporte.html", context)


# 🔹 4️⃣ Descargar ZIP con todos los documentos de un NC
def descargar_paquete(request, numero_control):
    soportes = Soporte.objects.filter(numero_control=numero_control)
    factura = Factura.objects.get(numero_control=numero_control)  # Solo una factura por NCI
    historias = HistoriaClinica.objects.filter(numero_control=numero_control)
    admisiones = Admision.objects.filter(numero_control=numero_control)

    # 🔹 Nombre del zip basado en el número de factura
    numero_factura = factura.numero_factura

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        # 🔹 Archivos físicos de soportes
        for soporte in soportes:
            if soporte.archivo and default_storage.exists(soporte.archivo.name):
                archivo_path = soporte.archivo.path
                nombre_archivo = f"{soporte.descripcion or soporte.get_tipo_display() or 'Soporte'}{os.path.splitext(soporte.archivo.name)[1]}"
                zf.write(archivo_path, nombre_archivo)

        # 🔹 PDF de la factura
        response_pdf = generar_factura_pdf(request, factura.id)
        nombre_pdf = factura.get_tipo_display() if hasattr(factura, 'get_tipo_display') else f"Factura_{factura.numero_factura}"
        zf.writestr(f"{nombre_pdf}.pdf", response_pdf.content)

        # 🔹 PDFs de historias clínicas
        for historia in historias:
            response_pdf = generar_historia_pdf(request, historia.id)
            nombre_pdf = historia.get_tipo_display() if hasattr(historia, 'get_tipo_display') else f"Historia_{historia.numero_control}"
            zf.writestr(f"{nombre_pdf}.pdf", response_pdf.content)

        # 🔹 PDFs de admisiones
        for admision in admisiones:
            response_pdf = generar_admision_pdf(request, admision.id)
            nombre_pdf = admision.get_tipo_display() if hasattr(admision, 'get_tipo_display') else f"Autorizacion_{admision.numero_control}"
            zf.writestr(f"{nombre_pdf}.pdf", response_pdf.content)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="documentos_{numero_factura}.zip"'
    return response

