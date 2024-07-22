from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_canonical_url(context):
    request = context.get('request', None)
    if request:
        scheme = request.scheme
        host = request.get_host()
        if not host.startswith('www.'):
            host = f'www.{host}'
        path = request.path
        return f'{scheme}://{host}{path}'
    else:
        return ''
