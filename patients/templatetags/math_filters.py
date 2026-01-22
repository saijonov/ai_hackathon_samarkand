from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def percentage(value):
    """Convert decimal to percentage (0.65 -> 65)"""
    try:
        return float(value) * 100
    except (ValueError, TypeError):
        return 0
