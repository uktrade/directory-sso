from django import template
from django.template.defaultfilters import stringfilter

from ..adapters import validate_next


register = template.Library()


@register.filter
@stringfilter
def is_valid_redirect_domain(domain):
    return validate_next(domain)
