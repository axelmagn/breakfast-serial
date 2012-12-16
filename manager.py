# django imports
from django.db.models import Manager
# local imports
from bserial.query import CacheQuerySet, AmazonQuerySet

class CacheManager(Manager):
    def get_query_set(self):
        return CacheQuerySet(self.model)
    def cache_add(self, obj, timeout=None, passive=False):
        self.get_query_set().cache_add(obj)


class AmazonManager(CacheManager):
    def get_query_set(self):
        return AmazonQuerySet(self.model)
    def lookup(self, *args, **kwargs):
        return self.get_query_set().lookup(*args, **kwargs)
    def search(self, *args, **kwargs):
        return self.get_query_set().search(*args, **kwargs)
