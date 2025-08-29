from django.db import models

class Tarifa(models.Model):
    codigo_cups = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo_cups} - {self.nombre}"

class Cie10(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"