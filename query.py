# stdlib imports
# django imports
from django.db.models.query import QuerySet
# 3rd party imports
# local imports

class ExtQuerySet(QuerySet):
    """
    Query set for a model that relies on external api calls as well.

    """


