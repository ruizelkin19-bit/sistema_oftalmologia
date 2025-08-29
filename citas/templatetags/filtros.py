# citas/templatetags/filtros.py

from django import template

register = template.Library()

@register.filter
def to_int(start, end):
    return range(start, end + 1)

def get_item(diccionario, clave):
    return diccionario.get(clave)