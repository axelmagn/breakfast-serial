# django imports
from django.db import models
# 3rd party imports
from bserial.manager import CacheManager

# Create your models here.

class CacheModel(models.Model):
    objects = CacheManager()
    def save(self):
        super(CacheModel, self).save()
        self.objects.cache_add(self)

class Book(CacheModel):
    """
    A Book to be referenced in our publications

    """
    asin = models.CharField(max_length=10, unique=True, db_index=True)
    title = models.CharField(max_length=128, blank=True, editable=False)
    author = models.CharField(max_length=128, blank=True, editable=False)

    def __unicode__(self):
        return "%s%s" % (
                self.title if self.title else self.asin,
                " by %s" if self.author else ""
        )

