from django import template

register = template.Library()


@register.filter
def subtract(value, arg):
    """Subtract arg from value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def multiply(value, arg):
    """Multiply value by arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """Divide value by arg."""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def percentage(value, total):
    """Calculate percentage."""
    try:
        return round(float(value) / float(total) * 100, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def currency(value):
    """Format as currency (BDT)."""
    try:
        return f"৳ {float(value):,.2f}"
    except (ValueError, TypeError):
        return "৳ 0.00"


@register.filter
def month_name(value):
    """Convert month number to name."""
    import calendar
    try:
        return calendar.month_name[int(value)]
    except (ValueError, TypeError, IndexError):
        return ''


@register.filter
def star_rating(value):
    """Convert score to star rating HTML."""
    try:
        score = int(float(value))
        full_stars = score
        empty_stars = 10 - score
        return '★' * full_stars + '☆' * empty_stars
    except (ValueError, TypeError):
        return '☆' * 10
