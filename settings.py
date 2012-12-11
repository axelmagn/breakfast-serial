from django.conf import settings
from django.core.cache import cache

# Cache to be used by default when storing models with additional attributes
DEFAULT_CACHE = getattr(settings, 'DEFAULT_CACHE', cache)

AMAZON_ACCESS_KEY_ID = getattr(
        settings,
        'AMAZON_ACCESS_KEY_ID',
        None
)
AMAZON_SECRET_KEY  = getattr(
        settings,
        'AMAZON_SECRET_KEY',
        None
)
AMAZON_ASSOC_TAG = getattr(
        settings,
        'AMAZON_ASSOC_TAG',
        None
)
