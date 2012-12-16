# 3rd party imports
from lxml import etree
import xpath
from bottlenose import Amazon
# local imports
from bserial.models import Book
from bserial.settings import (AMAZON_ACCESS_KEY_ID, AMAZON_SECRET_KEY,
                               AMAZON_ASSOC_TAG)

def _amazon():
    return Amazon(AMAZON_ACCESS_KEY_ID, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)

class XMLMapping(object):
    """
    XMLMapping class for mapping XML data to python objects for use in 
    populating model attributes

    """
    def __init__(self, selector):
        """Set up new XML Mapping"""
        super(XMLMapping, self).__init__()
        self.selector = selector

    def parse(self, node):
        """
        convert xml data in doc into a python object and return it.  Raise
        ValueError if the data is not present. (to be caught in most cases)
        

        Selects elements with xpath selector, then retrieves python value from
        parse_selections

        """
        # retrieve xpath selection
        selection = xpath.find(self.selector, node)
        # feed into parse_selection before returning
        return self.parse_selection(selection)

    def parse_selection(self, selection):
        """
        convert a list of dom elements into python object. 

        by default, returns selection

        override for functionality

        """
        return selection

    def __unicode__(self):
        return self.selector

class NodeMapping(XMLMapping):
    """
    force xpath selector to return a single node using xpath.findnode()

    """
    def parse(self, node):
        return xpath.findnode(self.selector, node)


class ValueMapping(XMLMapping):
    """
    force xpath selector to return values using xpath.findvalue()

    """
    def parse(self, node):
        return xpath.findvalue(self.selector, node)



class XMLInterface(object):
    """
    XMLInterface can map xml documents to lists of model instances

    """

    def __init__(self, *args, **kwargs):
        """
        Set up new XML interface objects

        Arguments:
        ----------

        Keywords:
        ---------
        model(class)=None        the model to translate into
        item_root(selector)="/"  selector for individual items
        map_strings(bool)=True   treat class strings as selectors
        map_default(class)=True  class to use for string selectors


        """

        # parse class definitions, using sane defaults
        self.model          = getattr(self, "model", None)
        self.item_root      = getattr(self, "item_root", XMLMapping("/"))
        self.map_strings    = getattr(self, "map_strings", True)
        self.map_default    = getattr(self, "map_default", XMLMapping)

        # override with init kwargs if present
        self.model          = kwargs.get("model", self.model)
        self.item_root      = kwargs.get("item_root", self.item_root)
        self.map_strings    = kwargs.get("map_strings", self.map_strings)
        self.map_default    = kwargs.get("map_default", self.map_default)


        accepted_selectors = [XMLMapping] # includes subclasses
        if self.map_strings:
            accepted_selectors += [str, unicode]

        class_dict = self.__class__.__dict__
        for key in class_dict:
            # don't map private attrs
            if not key.startswith('_'):
                value = class_dict[key]
                if self._is_valid_selector(value, accepted_selectors):
                    self.set_map(key, value)


    def _is_valid_selector(self, selector, accepted_types):
        return True in [isinstance(selector, t) for t in accepted_types]


    def set_map(self, key, selector):
        """Store a selector as an XMLMapping attribute"""
        # translate strings into instance XMLMapping attributes
        if isinstance(selector, str) or isinstance(selector, unicode):
            selector = self.map_default(selector)
            setattr(self, key, selector)
            return
        # translate XMLMappings into instance attributes
        elif isinstance(selector, XMLMapping):
            setattr(self, key, selector)
            return
        raise TypeError("Unrecognized Selector %s of type %s" % 
                        (selector, type(selector)))


    def get_maps(self):
        """Return all XMLMappings to be used in translation"""
        return {
                attr: selector for attr, selector in
                [(attr, getattr(self, attr)) for attr in self.__dict__]
                if isinstance(selector, XMLMapping)
        }


    def parse_model(self, doc):
        """
        Parse a model from a doc that represent exactly one item

        doc should typically be an element selected by item_root

        """
        # identify unique fields in the model
        unique_fields = [field.name for field in self.model._meta.fields
                         if field.unique]
        # retrieve those fields first from doc
        attrs = self.get_maps()
        init_kwargs = {key: attrs[key].parse(doc) for key in attrs 
                       if key in unique_fields}
        # get_or_create new model from unique fields
        out, is_created = self.model.objects.get_or_create(**init_kwargs)
        # fill in remaining attributes
        for key in attrs:
            if key not in unique_fields:
                # retrieve python object from parsed selector
                result = attrs[key].parse(doc)
                # omit empty results, but include False values
                if result not in[None, [], '']:
                    setattr(self, key, result)
        return out

    def parse(self, doc):
        out = []
        # iterate through items as defined by item_root
        for item in self.item_root.parse(doc):
            # parse model for item element
            out.append(self.parse_model(item))
        return out


class AmazonBookInterface(XMLInterface):
    """
    AmazonBookInterface queries Amazon Product API via bottlenose and converts
    the response into book objects.

    """

    def parse(self, *args, **kwargs):
        pass

    def _get_response(self, *args, **kwargs):
        """Query amazon for xml response"""
        pass

    def _get_item_lookup(self, **kwargs):
        """Query amazon for item lookup"""
        pass

    def _get_item_search(self, **kwargs):
        """Query amazon for item search"""
        pass

