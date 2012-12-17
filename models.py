# django imports
from django.db import models
# 3rd party imports
from bserial.manager import CacheManager, AmazonManager
from bserial.util import get_cache_key
from bserial.settings import DEFAULT_CACHE

class BookManager(CacheManager):
    use_for_related_fields = True

# Create your models here.
class Book(models.Model):
    """
    A Book to be referenced in our publications

    """
    asin = models.CharField(max_length=10, unique=True, db_index=True)
    title = models.CharField(max_length=128, blank=True, editable=False)
    author = models.CharField(max_length=128, blank=True, editable=False)

    objects = BookManager()
    amazon = AmazonManager()

    cache = DEFAULT_CACHE


    def _merge(self, obj, passive=True):
        """merge another object with self"""
        for attr in obj.__dict__:
            val = getattr(obj, attr)
            if not callable(val):
                if not (passive and hasattr(self, attr)):
                    setattr(self, attr, val)

    def get_cache(self, passive=False):
        """retrieve any cached items"""
        key = get_cache_key(self)
        obj = self.cache.get(key, None)
        if obj is not None:
            self._merge(obj, passive)

    @property
    def cached(self):
        self.get_cache()
        return self

    def __unicode__(self):
        return "%s%s" % (
                self.title if self.title else self.asin,
                " by " + self.author if self.author else ""
        )

