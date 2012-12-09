from django.core import settings, cache

# Cache to be used by default when storing models with additional attributes
DEFAULT_CACHE = getattr(settings, 'DEFAULT_CACHE', cache)

