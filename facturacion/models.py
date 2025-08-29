from django.db import models
from pacientes.models import Paciente
from citas.models import Cita
from decimal import Decimal, ROUND_HALF_UP

# import para señales
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Factura(models.Model):
    ESTADOS = [
        ('facturada', 'Facturada'),
        ('anulada', 'Anulada'),
    ]

    FORMAS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('otro', 'Otro'),
    ]

    cita = models.OneToOneField(Cita, on_delete=models.CASCADE, related_name='factura')
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)

    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='facturada')

    numero_control = models.CharField(max_length=51, unique=True, blank=True, editable=False)
    numero_factura = models.CharField(max_length=20, unique=True, blank=True, editable=False)

    forma_pago = models.CharField(max_length=50, choices=FORMAS_PAGO)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    impuestos = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=Decimal('0.00'))

    iva_aplica = models.BooleanField(default=False)
    copago = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cuota_moderadora = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    bonos = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    observaciones = models.TextField(blank=True, null=True)
    valor_letras = models.CharField(max_length=255, blank=True, null=True)

    def generar_numero_control(self):
        ultima = Factura.objects.order_by('-id').first()
        consecutivo = 0
        if ultima and ultima.numero_control and ultima.numero_control.startswith("NCI-"):
            try:
                consecutivo = int(ultima.numero_control.replace("NCI-", ""))
            except ValueError:
                pass
        return f"NCI-{(consecutivo + 1):06d}"

    def generar_numero_factura(self):
        ultima = Factura.objects.order_by('-id').first()
        consecutivo = 0
        if ultima and ultima.numero_factura and ultima.numero_factura.startswith("FV-"):
            try:
                consecutivo = int(ultima.numero_factura.replace("FV-", ""))
            except ValueError:
                pass
        return f"FV-{(consecutivo + 1):08d}"

    def calcular_totales(self):
        detalles = self.detalles.all()

        subtotal = Decimal('0.00')
        descuentos = Decimal('0.00')
        impuestos = Decimal('0.00')

        for d in detalles:
            subtotal += d.cantidad * d.valor_unitario
            descuentos += d.descuento or Decimal('0.00')
            impuestos += d.iva or Decimal('0.00')

        # Total de la factura: subtotal - descuentos + sumatoria de IVA de detalles - ajustes manuales
        total = (subtotal - descuentos) + impuestos - (self.copago + self.cuota_moderadora + self.bonos)

        # Redondeo final
        self.subtotal = subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.descuento = descuentos.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.impuestos = impuestos.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.total = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def save(self, *args, **kwargs):
        if not self.numero_control:
            self.numero_control = self.generar_numero_control()
        if not self.numero_factura:
            self.numero_factura = self.generar_numero_factura()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Factura {self.numero_factura} - {self.paciente.nombre}'

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ['-fecha']


class FacturaDetalle(models.Model):
    factura = models.ForeignKey(Factura, related_name='detalles', on_delete=models.CASCADE)
    codigo = models.CharField(max_length=50)
    producto = models.CharField(max_length=255)
    cantidad = models.PositiveIntegerField(default=1)
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    iva = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def calcular_total(self):
        self.total = (self.cantidad * self.valor_unitario - self.descuento + self.iva).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return self.total

    @property
    def subtotal_detalle(self):
        return (self.cantidad * self.valor_unitario - self.descuento + self.iva).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def save(self, *args, **kwargs):
        self.calcular_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.producto} ({self.cantidad})'


# Señales para recalcular factura al agregar/editar/borrar un detalle
@receiver(post_save, sender=FacturaDetalle)
def _on_detalle_saved(sender, instance, **kwargs):
    factura = instance.factura
    factura.calcular_totales()
    factura.save(update_fields=['subtotal', 'descuento', 'impuestos', 'total'])


@receiver(post_delete, sender=FacturaDetalle)
def _on_detalle_deleted(sender, instance, **kwargs):
    factura = instance.factura
    factura.calcular_totales()
    factura.save(update_fields=['subtotal', 'descuento', 'impuestos', 'total'])
