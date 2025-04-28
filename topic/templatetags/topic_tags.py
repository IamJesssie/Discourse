from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def comma_split(value):
    """Split a string by commas and return a list"""
    return [tag.strip() for tag in value.split(',') if tag.strip()]