class NoIndexMixin:
    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        response['X-Robots-Tag'] = 'noindex'
        return response
