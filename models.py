# django imports
from django.db import models
# 3rd party imports
from bserial.manager import CacheManager, AmazonManager

# Create your models here.
class Book(models.Model):
    """
    A Book to be referenced in our publications

    """
    asin = models.CharField(max_length=10, unique=True, db_index=True)
    title = models.CharField(max_length=128, blank=True, editable=False)
    author = models.CharField(max_length=128, blank=True, editable=False)

    objects = CacheManager()
    amazon = AmazonManager()

    def __unicode__(self):
        return "%s%s" % (
                self.title if self.title else self.asin,
                " by " + self.author if self.author else ""
        )

