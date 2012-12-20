# django imports
from django.db import models
# 3rd party imports
from bserial.manager import CacheManager, AmazonManager
from bserial.util import merge_objects

# Create your models here.
class Book(models.Model):
    """
    A Book to be referenced in our publications

    """
    asin = models.CharField(max_length=10, unique=True, db_index=True)
    title = models.CharField(max_length=128, blank=True, editable=False)
    author = models.CharField(max_length=128, blank=True, editable=False)

    cover_lg_url = models.TextField(null=True, blank=True)
    cover_md_url = models.TextField(null=True, blank=True)
    cover_sm_url = models.TextField(null=True, blank=True)

    description = models.TextField(null=True, blank=True)
    detail_page_url = models.TextField(null=True, blank=True)

    objects = CacheManager()
    amazon = AmazonManager()


    @property
    def cached(self):
        return self.__class__.objects.get(pk=self.pk)


    def lookup(self, *args, **kwargs):
        args = (self.asin,) + args
        bl = self.__class__.amazon.lookup(*args, **kwargs)[0]
        merge_objects(self, bl)

    def __unicode__(self):
        return "%s%s" % (
                self.title if self.title else self.asin,
                " by " + self.author if self.author else ""
        )

