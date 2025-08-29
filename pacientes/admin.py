from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.contrib import messages
from .models import Paciente
from .forms_excel import CargarExcelPacientesForm
import openpyxl
from django.template.response import TemplateResponse
from datetime import datetime
from .models import Pais, Departamento, Municipio

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',  # sigue mostrando el nombre en la tabla admin
        'numDocumentoIdentificacion',  # nuevo campo obligatorio
        'telefono',
        'correo',
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('cargar-excel/', self.admin_site.admin_view(self.cargar_excel_view), name='paciente-cargar-excel'),
        ]
        return custom_urls + urls

    def cargar_excel_view(self, request):
        if request.method == 'POST':
            form = CargarExcelPacientesForm(request.POST, request.FILES)
            if form.is_valid():
                archivo = request.FILES['archivo_excel']
                try:
                    wb = openpyxl.load_workbook(archivo)
                    hoja = wb.active
                    for fila in hoja.iter_rows(min_row=2, values_only=True):
                        (
                            fecha_registro,
                            nombre,
                            tipo_doc,
                            num_doc,
                            tipo_usuario,
                            fecha_nacimiento,
                            sexo,
                            pais_residencia,
                            municipio_residencia,
                            zona_territorial,
                            pais_origen,
                            telefono,
                            correo,
                            direccion
                        ) = fila

                        if not num_doc:
                            continue  # si no hay documento, se salta la fila

                        Paciente.objects.update_or_create(
                            numDocumentoIdentificacion=num_doc,
                            defaults={
                                'fecha_registro': fecha_registro or datetime.today(),
                                'nombre': nombre or '',
                                'tipoDocumentoIdentificacion': tipo_doc,
                                'tipoUsuario': tipo_usuario,
                                'fechaNacimiento': fecha_nacimiento,
                                'codSexo': sexo,
                                'codPaisResidencia': pais_residencia,
                                'codMunicipioResidencia': municipio_residencia,
                                'codZonaTerritorialResidencia': zona_territorial,
                                'codPaisOrigen': pais_origen,
                                'telefono': telefono,
                                'correo': correo,
                                'direccion': direccion
                            }
                        )

                    self.message_user(request, "Pacientes cargados exitosamente.", level=messages.SUCCESS)
                    return redirect('admin:pacientes_paciente_changelist')

                except Exception as e:
                    self.message_user(request, f"Error al cargar el archivo: {e}", level=messages.ERROR)

        else:
            form = CargarExcelPacientesForm()

        context = dict(
            self.admin_site.each_context(request),
            form=form,
            title='Cargar pacientes desde Excel',
        )
        return TemplateResponse(request, "admin/cargar_excel_admin.html", context)

@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ('codigo_dane', 'nombre')
    search_fields = ('nombre', 'codigo_dane')

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('nombre', 'codigo')

@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('codigo_dane', 'nombre', 'departamento')
    search_fields = ('nombre', 'codigo_dane')
    list_filter = ('departamento',)