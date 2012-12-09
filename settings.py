from django.conf import settings

CACHE_NAME = getattr(settings, 'CACHE_NAME', "default")
