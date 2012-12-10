from django.conf import settings
from django.core import cache

# Cache to be used by default when storing models with additional attributes
DEFAULT_CACHE = getattr(settings, 'DEFAULT_CACHE', cache)

