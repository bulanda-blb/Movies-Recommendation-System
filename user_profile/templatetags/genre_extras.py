from django import template

register = template.Library()

@register.filter
def humanize_genre(value):
    """
    Replace hyphens with spaces and title‐case.
    e.g. "sci-fi" -> "Sci Fi"
    """
    if not isinstance(value, str):
        return value
    return value.replace('-', ' ').title()
