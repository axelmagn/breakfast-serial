# django imports
from django.db.models import Manager
# local imports
from bserial.query import CacheQuerySet

class CacheManager(Manager):
    def get_query_set(self):
        return CacheQuerySet(self.model)
    def cache_add(self, obj, timeout=None, passive=False):
        self.get_query_set().cache_add(obj)
