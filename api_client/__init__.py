from django.conf import settings
from django.utils.module_loading import import_string


ClientClass = import_string(settings.DIRECTORY_API_EXTERNAL_CLIENT_CLASS)
api_client = ClientClass(
    base_url=settings.DIRECTORY_API_EXTERNAL_CLIENT_BASE_URL,
    api_key=settings.DIRECTORY_API_EXTERNAL_SIGNATURE_SECRET,
)
