# citas/templatetags/rangos.py

from django import template
register = template.Library()

@register.filter
def to_range(start, end):
    return range(start, end)
