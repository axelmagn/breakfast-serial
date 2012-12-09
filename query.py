# stdlib imports
# django imports
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet

# 3rd party imports
# local imports
from bserial.settings import DEFAULT_CACHE
from bserial.util import merge_objects

class ExtQuerySet(QuerySet):
    """
    Query set for a model that relies on external api calls as well.

    Because models have attributes that are stored outside of the database,
    models with these extra attributes are cached so that other query sets can
    retrieve them.

    """
    def __init__(self, models=None, query=None, using=None, 
                 cache=DEFAULT_CACHE, timeout=30):
        super(ExtQuerySet, self).__init__(self, models, query, using)
        self.cache = cache
        self.timeout = timeout
    def _cache_key(self, obj):
        """construct the cache key of an appropriate object"""
        # use color separator, as it's an illegal character in class name
        ct = ContentType.objects.get_for_model(obj)
        return "%s,%s,%s" % (ct.app_name, ct.name, obj.pk)
    def cache_add(self, obj, timeout=None):
        """store an object in the cache for later retrieval"""
        # make sure object is the correct type
        if not isinstance(obj, self.model):
            raise TypeError("%s is not a model in this QuerySet." % obj)
        # get storage key
        key = self._cache_key(obj)
        # retrieve already cached object, if any
        cached_obj = self.cache.get(key, None)
        if cached_obj:
            # merge cached object into object
            obj = merge_objects(obj, cached_obj)
        self.cache.set(key, obj, timeout)
