# stdlib imports
from copy import deepcopy
# django imports
from django.db.models.query import QuerySet
# 3rd party imports
# local imports
from bserial.settings import DEFAULT_CACHE
from bserial.util import merge_objects, get_cache_key




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
        return get_cache_key(obj)


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

    def get(self, *args, **kwargs):
        out = super(CacheQuerySet, self).get(*args, **kwargs)
        return self._cache_get(out)


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
    _max_results = 10

    def __init__(self, model=None, query=None, using=None, 
                 cache=DEFAULT_CACHE, timeout=30):
        super(AmazonQuerySet, self).__init__(model, query, using, cache, 
                                            timeout)
        # deferred import because bserial.serial uses Book model
        from bserial.serial import AmazonBookInterface
        self.amazon = AmazonBookInterface()

        
    def lookup(self, *args, **kwargs):
        # if no id's specified, use books in this queryset
        if not args and not kwargs.has_key("ItemId"):
            kwargs["ItemId"] = [
                    book.asin for book in self.all()[:self._max_results]
            ]
        # perform lookup.  books is a list.  no results => empty
        books = self.amazon.lookup(*args, **kwargs)
        # cache results
        for book in books:
            self.cache_add(book)
        return books

    def batch_lookup(self, *args, **kwargs):
        """
        DANGEROUS!
        same as lookup, but performs multiple queries for large counts
        
        It will keep sending amazon api requests, regardless of how many books
        are out there.
        """
        # if no id's specified, use books in this queryset
        if not args and not kwargs.has_key("ItemId"):
            kwargs["ItemId"] = [
                    book.asin for book in self.all()
            ]
        books = []
        # iterate through item ids in steps, performing a lookup for each
        for seg_index in xrange(0,len(kwargs["ItemId"]), self._max_results):
            seg_ciel = seg_index + self._max_results
            seg_ids = kwargs["ItemId"][seg_index:seg_ciel]
            seg_kwargs = deepcopy(kwargs)
            seg_kwargs["ItemId"] = seg_ids
            seg_books = self.amazon.lookup(*args, **seg_kwargs)
            books += seg_books
        # cache results
        for book in books:
            self.cache_add(book)
        return books

            
    

    def search(self, *args, **kwargs):
        books = self.amazon.search(*args, **kwargs)
        for book in books:
            self.cache_add(book)
        return books
