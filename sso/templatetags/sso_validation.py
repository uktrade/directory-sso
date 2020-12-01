from django import template
from django.template.defaultfilters import stringfilter

from ..adapters import is_valid_redirect

register = template.Library()


@register.filter
@stringfilter
def is_valid_redirect_domain(domain):
    return is_valid_redirect(domain)
