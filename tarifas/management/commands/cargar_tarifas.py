import json
from django.core.management.base import BaseCommand
from tarifas.models import Tarifa

class Command(BaseCommand):
    help = 'Carga las tarifas CUPS oftalmológicas desde un archivo JSON'

    def handle(self, *args, **kwargs):
        with open('tarifas/fixtures/cups_oftalmologia.json', 'r', encoding='utf-8') as file:
            datos = json.load(file)
            for item in datos:
                tarifa, creado = Tarifa.objects.update_or_create(
                    codigo_cups=item['codigo_cups'],
                    defaults={
                        'nombre': item['nombre'],
                        'descripcion': item['descripcion'],
                        'valor': item['valor'],
                        'activo': item['activo']
                    }
                )
                estado = "creado" if creado else "actualizado"
                self.stdout.write(self.style.SUCCESS(f"Tarifa {estado}: {tarifa.codigo_cups} - {tarifa.nombre}"))
