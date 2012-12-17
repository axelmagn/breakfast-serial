"""
Utility objects and methods for BreakfastSerial

"""
# stdlib imports
from copy import deepcopy
# django imports
from django.contrib.contenttypes.models import ContentType

def merge_objects(*args):
    """
    Take a list of objects and merge their attributes.

    Objects listed first take precedence over objects listed after.  All
    objects must be the same type.

    """
    if len(args) < 2:
        raise ValueError("Must provide at least two objects in arguments")
    tgt = deepcopy(args[0])
    for src in args[1:]:
        if not isinstance(src, type(tgt)):
            raise TypeError("%s is not of the type %s" % (src, type(tgt)))
        for property in src.__dict__:
            # check to make sure it can't be called (a method)
            # also check that tgt doesn't have a property of the same name
            if (not callable(src.__dict__[property]) and
                    not hasattr(tgt, property)):
                setattr(tgt, property, getattr(src, property))
    return tgt

def get_cache_key(obj):
    """construct the cache key of an appropriate object"""
    # use comma separator, as it's an illegal character in class name
    ct = ContentType.objects.get_for_model(obj)
    return "%s,%s,%s" % (ct.app_label, ct.name, obj.pk)
