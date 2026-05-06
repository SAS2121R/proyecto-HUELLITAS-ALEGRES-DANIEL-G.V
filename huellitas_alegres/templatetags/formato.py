from django import template

register = template.Library()


@register.filter(name='pesos')
def pesos(value):
    """Format a number as Colombian pesos with dots as thousands separator.
    Example: 85000 → $85.000 | 1250000 → $1.250.000 | 0 → $0
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        return '$0'
    # Format with dots as thousands separator (no decimals for pesos)
    formatted = f'{value:,}'.replace(',', '.')
    return f'${formatted}'


@register.filter(name='miles')
def miles(value):
    """Format a number with dots as thousands separator, no currency symbol.
    Example: 85000 → 85.000
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        return '0'
    return f'{value:,}'.replace(',', '.')