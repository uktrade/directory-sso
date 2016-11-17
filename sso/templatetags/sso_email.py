from django import template
from django.core.urlresolvers import reverse, resolve
from sso import constants

register = template.Library()


@register.simple_tag
def header_image():
    return constants.EMAIL_HEADER_IMAGE


@register.simple_tag
def absolute_url(name):
    url = reverse(name)
    view = resolve(url)
    return view.func.view_initkwargs['url']
