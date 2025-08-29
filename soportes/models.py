from django.db import models
import os

class Soporte(models.Model):
    TIPOS_SOPORTE = [
        ('factura', 'Factura'),
        ('admision', 'Admisión'),
        ('historia', 'Historia clínica'),
        ('autorizacion', 'Autorización'),
        ('orden', 'Orden médica'),
        ('examen', 'Examen'),
        ('otro', 'Otro'),
    ]

    # Amarre directo con el número de control (string único)
    numero_control = models.CharField(
        max_length=20,
        db_index=True,
        help_text="Número de control interno que agrupa todos los soportes."
    )

    tipo = models.CharField(
        max_length=50,
        choices=TIPOS_SOPORTE,
        help_text="Tipo de documento asociado al número de control."
    )

    def ruta_soporte(instance, filename):
        """
        Carpeta dinámica basada en el número de factura asociada al NCI.
        Ej: MEDIA_ROOT/soportes/FV-00000002/archivo.pdf
        """
        from facturacion.models import Factura

        try:
            factura = Factura.objects.get(numero_control=instance.numero_control)
            carpeta = f"soportes/{factura.numero_factura}"
        except Factura.DoesNotExist:
            carpeta = "soportes/sin_factura"

        # Solo el nombre del archivo, sin subcarpetas previas
        return os.path.join(carpeta, os.path.basename(filename))

    archivo = models.FileField(
        upload_to=ruta_soporte,
        help_text="Archivo PDF o imagen del soporte."
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción adicional del soporte."
    )

    fecha_carga = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_carga"]  # Los más recientes arriba
        verbose_name = "Soporte"
        verbose_name_plural = "Soportes"
        indexes = [
            models.Index(fields=["numero_control"]),  # Optimiza búsquedas por NC
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - NC {self.numero_control}"

    @property
    def nombre_archivo(self):
        """Devuelve el nombre del archivo sin la ruta completa."""
        return os.path.basename(self.archivo.name)