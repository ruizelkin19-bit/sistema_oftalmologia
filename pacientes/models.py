from django.db import models
from django.utils import timezone
from datetime import date

NIVEL_INGRESO_SM = {
    '1': 2,     # Nivel 1: hasta 2 SM
    '2': 4,     # Nivel 2: hasta 4 SM
    '3': 6,     # Nivel 3: hasta 6 SM
    '4': 9999,  # Nivel 4: ingresos altos
}

class Pais(models.Model):
    codigo_dane = models.CharField(max_length=3, unique=True, verbose_name="Código DANE")
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del país")

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Paises"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.codigo_dane})"


class Departamento(models.Model):
    codigo = models.CharField(max_length=2, unique=True)
    nombre = models.CharField(max_length=100)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class Municipio(models.Model):
    codigo_dane = models.CharField(max_length=5, unique=True)
    nombre = models.CharField(max_length=100)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class Paciente(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de ciudadanía'),
        ('TI', 'Tarjeta de identidad'),
        ('RC', 'Registro civil'),
        ('CE', 'Cédula de extranjería'),
        ('PA', 'Pasaporte'),
    ]

    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    # ✅ Solo valores válidos
    TIPO_USUARIO_RIPS_CHOICES = [
        ('C', 'Cotizante'),
        ('B', 'Beneficiario'),
    ]

    ZONA_RESIDENCIA_CHOICES = [
        ('U', 'Urbana'),
        ('R', 'Rural'),
    ]

    # ✅ Usamos letras diferentes para que no choque con tipoUsuario
    REGIMEN_CHOICES = [
        ('CO', 'Contributivo'),
        ('SU', 'Subsidiado'),
        ('ES', 'Especial'),
        ('OT', 'Otro'),
    ]

    NIVEL_CHOICES = [
        ('1', 'Nivel 1'),
        ('2', 'Nivel 2'),
        ('3', 'Nivel 3'),
        ('4', 'Nivel 4'),
    ]

    CLASE_SERVICIO_CHOICES = [
        ('CONS', 'Consulta'),
        ('URG', 'Urgencias'),
        ('HOSP', 'Hospitalización'),
        ('MED', 'Medicamentos'),
    ]

    # Datos de identificación
    tipoDocumentoIdentificacion = models.CharField(
        "Tipo de Documento", max_length=2,
        choices=TIPO_DOCUMENTO_CHOICES,
        blank=True, null=True
    )
    numDocumentoIdentificacion = models.CharField(
        "Número de Documento", max_length=20,
        unique=True, blank=True, null=True
    )

    primer_nombre = models.CharField("Primer Nombre", max_length=50, blank=True, null=True)
    segundo_nombre = models.CharField("Segundo Nombre", max_length=50, blank=True, null=True)
    primer_apellido = models.CharField("Primer Apellido", max_length=50, blank=True, null=True)
    segundo_apellido = models.CharField("Segundo Apellido", max_length=50, blank=True, null=True)

    nombre = models.CharField("Nombre Completo", max_length=200, editable=False, default='')

    fechaNacimiento = models.DateField("Fecha de Nacimiento", blank=True, null=True)
    codSexo = models.CharField("Sexo", max_length=1, choices=SEXO_CHOICES, blank=True, null=True)

    # Contacto
    telefono = models.CharField("Teléfono", max_length=20, blank=True, null=True)
    correo = models.EmailField("Correo electrónico", blank=True, null=True)
    direccion = models.CharField("Dirección", max_length=200, blank=True, null=True)

    departamentoResidencia = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Departamento de Residencia"
    )
    codMunicipioResidencia = models.ForeignKey(
        Municipio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Municipio de Residencia"
    )

    # Información de salud
    tipoUsuario = models.CharField(
        "Tipo de Usuario (RIPS)", max_length=1,
        choices=TIPO_USUARIO_RIPS_CHOICES,
        blank=True, null=True
    )
    regimen = models.CharField(
        "Régimen de afiliación", max_length=2,  # ← ahora diferente
        choices=REGIMEN_CHOICES, blank=True, null=True
    )
    nivel = models.CharField(
        "Nivel de ingresos", max_length=1,
        choices=NIVEL_CHOICES, blank=True, null=True
    )
    ingreso_salarios_minimos = models.DecimalField(
        "Ingreso aproximado (SM)", max_digits=10, decimal_places=2,
        blank=True, null=True,
        help_text="Se calcula automáticamente según el nivel, nivel 4 si ingresos >6 SM"
    )
    clase_servicio = models.CharField(
        "Clase de Servicio", max_length=10,
        choices=CLASE_SERVICIO_CHOICES, default='CONS'
    )

    codZonaTerritorialResidencia = models.CharField(
        max_length=1,
        choices=ZONA_RESIDENCIA_CHOICES,
        verbose_name="Zona territorial de residencia",
        blank=True, null=True
    )

    codPaisResidencia = models.ForeignKey(
        'Pais',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='residencias',
        verbose_name="País de residencia"
    )

    codPaisOrigen = models.ForeignKey(
        'Pais',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='origenes',
        verbose_name="País de origen"
    )

    fecha_registro = models.DateTimeField("Fecha de Registro", default=timezone.now)

    def save(self, *args, **kwargs):
        # Nombre completo
        partes = filter(None, [
            self.primer_nombre,
            self.segundo_nombre,
            self.primer_apellido,
            self.segundo_apellido
        ])
        self.nombre = " ".join(partes)

        # Asignar ingreso automáticamente según nivel
        if self.tipoUsuario == 'C':  # Cotizante
            if self.nivel:
                self.ingreso_salarios_minimos = NIVEL_INGRESO_SM.get(self.nivel)
            else:
                # Si gana más de 6 SM, nivel 4
                if self.ingreso_salarios_minimos and self.ingreso_salarios_minimos > 6:
                    self.nivel = '4'

        super().save(*args, **kwargs)

    @property
    def edad(self):
        if self.fechaNacimiento:
            today = date.today()
            return today.year - self.fechaNacimiento.year - (
                (today.month, today.day) < (self.fechaNacimiento.month, self.fechaNacimiento.day)
            )
        return None

    def __str__(self):
        return f"{self.nombre}"
