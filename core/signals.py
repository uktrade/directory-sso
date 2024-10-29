from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, weak=False)
def clear_the_cache(**kwargs):
    '''
    We have implemented Django caching middleware. By default, this caches all GET requests.

    This signal will invalidate the cache when a model is saved request.
    '''
    cache.clear()
