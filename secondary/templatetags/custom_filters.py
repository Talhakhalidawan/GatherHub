from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """Add a CSS class to a form field."""
    return field.as_widget(attrs={'class': css_class})

@register.filter(name='add_id')
def add_id(field, css_id):
    """Add an ID to a form field."""
    return field.as_widget(attrs={'id': css_id})