# stdlib imports
# django imports
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet

# 3rd party imports
# local imports
from bserial.settings import DEFAULT_CACHE
from bserial.util import merge_objects




class CacheQuerySet(QuerySet):
    """
    Query set for a model that relies on external api calls as well.

    Because models have attributes that are stored outside of the database,
    models with these extra attributes are cached so that other query sets can
    retrieve them.

    """
    def __init__(self, model=None, query=None, using=None, 
                 cache=DEFAULT_CACHE, timeout=30):
        super(CacheQuerySet, self).__init__(model, query, using)
        self.cache = cache
        self.timeout = timeout


    def _cache_key(self, obj):
        """construct the cache key of an appropriate object"""
        # use color separator, as it's an illegal character in class name
        ct = ContentType.objects.get_for_model(self.model)
        return "%s,%s,%s" % (ct.app_label, ct.name, obj.pk)


    def cache_add(self, obj, timeout=None, passive=False):
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
            if  passive:
                obj = merge_objects(cached_obj, obj)
            else:
                obj = merge_objects(obj, cached_obj)
        # make sure that db and cache match
        obj.save()
        # cache pickled object
        self.cache.set(key, obj, timeout)


    def _cache_get(self, obj, passive=False):
        """retrieve object from cache, if any, and merge data"""
        key = self._cache_key(obj)
        cached_obj = self.cache.get(key, None)
        if cached_obj:
            if passive:
                return merge_objects(cached_obj, obj)
            else:
                return merge_objects(obj, cached_obj)
        return obj


    def __getitem__(self, k):
        """
        Retrieves an item or slice from the set of results, and merges it with
        any cached results

        """
        out = super(CacheQuerySet, self).__getitem__(k)
        if isinstance(out, list):
            return [self._cache_get(obj) for obj in out]
        elif isinstance(out, self.model):
            return self._cache_get(out)
        return out
    



class AmazonQuerySet(CacheQuerySet):
    """
    QuerySet that can retrieve items from amazon api

    """

    def __init__(self, model=None, query=None, using=None, 
                 cache=DEFAULT_CACHE, timeout=30):
        super(AmazonQuerySet, self).__init__(model, query, using, cache, 
                                            timeout)
        # deferred import because bserial.serial uses Book model
        AmazonBookInterface = __import__(
                'bserial.serial',
                globals(), locals(),
                ['AmazonBookInterface'], -1
        ).AmazonBookInterface
        self.amazon = AmazonBookInterface()

        
    def lookup(self, *args, **kwargs):
        books = self.amazon.lookup(*args, **kwargs)
        for book in books:
            self.cache_add(book)
        return books
    

    def search(self, *args, **kwargs):
        books = self.amazon.search(*args, **kwargs)
        for book in books:
            self.cache_add(book)
        return books
    
