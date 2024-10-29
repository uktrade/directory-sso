import logging

from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, weak=False)
def clear_the_cache(**kwargs):
    '''
    We have implemented Django caching middleware. By default, this caches all GET requests.

    This signal will invalidate the cache when a model is saved request.
    '''
    if settings.DEBUG:
        logger.info('.save() model has been invoked - attempting cache.clear() call')
    cache.clear()
    if settings.DEBUG:
        logger.info('cache.clear() call complete')
