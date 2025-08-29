from django import template

register = template.Library()

@register.filter
def to_range(start, end):
    """
    Retorna un rango de enteros desde start hasta end-1.
    Ejemplo: {{ 1|to_range:5 }} genera [1,2,3,4]
    """
    try:
        start = int(start)
        end = int(end)
    except (ValueError, TypeError):
        return []

    return range(start, end)
