# 3rd party imports
from bottlenose import Amazon
from xml.dom.minidom import parseString
import xpath
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

    def __repr__(self):
        return "<%s: %s>" % (self.__class__, self.__unicode__())

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




class BooleanMapping(XMLMapping):
    """Interprets value as boolean"""
    def parse(self, node):
        selection = xpath.findvalue(self.selector, node)
        return selection.lower() in ["true", "1", 'yes', 'y']




class MultiValueMapping(XMLMapping):
    """
    value mapping for every element returned by selector

    """
    valmap = ValueMapping("self::*")

    def parse_selection(self, selection):
        return [self.valmap.parse(el) for el in selection]




class CSVMapping(MultiValueMapping):
    """Return list of values as comma separated string"""

    def parse_selection(self, selection):
        return ",".join(super(CSVMapping, self).parse_selection(selection))




class DictMapping(XMLMapping):
    """
    lazy XML Interface. returns a list of attribute dicts

    Arguments:
    ----------
    0       item_root       selector to return list of elements
    1       attr_dict       for each element, create dict with these attrs

    attr_dict values should all be XMLMappings.
    output dicts will be the results of these mappings, if present

    """

    def __init__(self, item_root, attr_dict):
        self.item_root = item_root
        self.attr_dict = attr_dict

    def parse(self, node):
        out = []
        items = self.item_root.parse(node)
        for item in items:
            attrs = {}
            for attr in self.attr_dict:
                value = self.attr_dict[attr].parse(item)
                if value not in [None, [], '']:
                    attrs[attr] = value
            out.append(attrs)
        return out






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
                if isinstance(selector, XMLMapping) and attr != "item_root"
        }


    def parse_model(self, doc):
        """
        Parse a model from a doc that represent exactly one item

        doc should typically be an element selected by item_root

        """
        # import pdb; pdb.set_trace()     #DEBUG
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
                    setattr(out, key, result)
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

    model       = Book
    item_root   = XMLMapping("/*/Items/Item")
    map_default = ValueMapping

    # defaults
    _search_index = "KindleStore"
    _method = "lookup"
    _is_valid = BooleanMapping("/*/Items/Request/IsValid")
    _error_code = ValueMapping("/*/Items/Request/Errors/Error/Code")
    _error_msg = ValueMapping("/*/Items/Request/Errors/Error/Message")

    # intermediate mappings
    _img_url        = ValueMapping("URL")
    _img_height     = ValueMapping("Height")
    _img_hunits     = ValueMapping("Height/@Units")
    _img_width      = ValueMapping("Width")
    _img_wunits     = ValueMapping("Width/@Units")
    _img_md         = XMLMapping("MediumImage")
    _img_lg         = XMLMapping("LargeImage")

    # basic attributes
    asin = "ASIN"
    title = "ItemAttributes/Title"
    author = CSVMapping("ItemAttributes/Author")
    # ResponseGroup:    Images
    small_image = DictMapping(
            XMLMapping("SmallImage"),
            {
                "url":              _img_url,
                "height":           _img_height,
                "height_units":     _img_hunits,
                "width":            _img_width,
                "width_units":      _img_wunits,
            }
    )
    medium_image = DictMapping(
            XMLMapping("MediumImage"),
            {
                "url":              _img_url,
                "height":           _img_height,
                "height_units":     _img_hunits,
                "width":            _img_width,
                "width_units":      _img_wunits,
            }
    )
    large_image = DictMapping(
            XMLMapping("LargeImage"),
            {
                "url":              _img_url,
                "height":           _img_height,
                "height_units":     _img_hunits,
                "width":            _img_width,
                "width_units":      _img_wunits,
            }
    )
    # ResponseGroup:    EditorialReview
    description = ValueMapping("EditorialReviews/EditorialReview[1]/Content" +
                               '[../Source/text() = "Product Description"]')


    def parse(self, *args, **kwargs):
        """
        Query amazon for xml response

        Arguments:
        ----------
        0   ItemId(s)       csv string of item id(s)    if method=lookup
        0   Keywords        keyword search string       if method=search
        1   ResponseGroup   amazon api response group
        
        Keywords:
        ---------
        method(string)=lookup       what sort of query to send to amazon

        """
        doc = parseString(self._get_response(*args, **kwargs))
        self._validate(doc)
        return super(AmazonBookInterface, self).parse(doc)


    def lookup(self, *args, **kwargs):
        """
        Query amazon for item lookup
        
        Arguments:
        ----------
        0   ItemId(s)       csv string of item id(s)
        1   ResponseGroup   amazon api response group

        kwargs are fed directly into bottlenose

        """
        doc = parseString(self._item_lookup_response(*args, **kwargs))
        self._validate(doc)
        return super(AmazonBookInterface, self).parse(doc)


    def search(self, *args, **kwargs):
        """
        Query amazon for item search
        
        Arguments:
        ----------
        0   Keywords    keyword search string
        1   ResponseGroup   amazon api response group

        Keywords are fed directly into bottlenose.

        """
        doc = parseString(self._item_search_response(*args, **kwargs))
        self._validate(doc)
        return super(AmazonBookInterface, self).parse(doc)


    def _validate(self, doc):
        is_valid = self._is_valid.parse(doc)
        if not is_valid:
            code = self._error_code.parse(doc)
            msg = self._error_msg.parse(doc)
            raise RuntimeError("Amazon Errror %s: %s" % (code, msg))


    def _get_response(self, *args, **kwargs):
        method = kwargs.pop("method", self._method).lower()
        if method == 'lookup':
            return self._item_lookup_response(*args, **kwargs)
        if method == 'search':
            return self._item_search_response(*args, **kwargs)
        raise ValueError("Unknown mehod Keyword: %s" % method)


    def _item_lookup_response(self, *args, **kwargs):
        if args:
            # make sure kwargs[ItemId] is empty before storing new value
            item_id = kwargs.get("ItemId", None)
            if item_id is None:
                kwargs["ItemId"] = args[0]
            else:
                raise RuntimeError("Cannot have keyword ItemId AND provide " +
                                   "an argument")
        if len(args) > 1:
            # make sure kwargs[ResponseGroup] is empty before storing new val
            response_group = kwargs.get("ResponseGroup", None)
            if response_group is None:
                kwargs["ResponseGroup"] = args[1]
            else:
                raise RuntimeError("Cannot have keyword ResponseGroup AND " + 
                                   "provide a second argument")
        return _amazon().ItemLookup(**kwargs)


    def _item_search_response(self, *args, **kwargs):
        kwargs['SearchIndex'] = kwargs.get('SearchIndex', self._search_index)
        if args:
            # make sure kwargs[Keywords] is empty before storing new value
            keywords = kwargs.get("Keywords", None)
            if keywords is None:
                kwargs["Keywords"] = args[0]
            else:
                raise RuntimeError("Cannot have keyword 'Keywords' AND " +
                                   "provide an argument")
        if len(args) > 1:
            # make sure kwargs[ResponseGroup] is empty before storing new val
            response_group = kwargs.get("ResponseGroup", None)
            if response_group is None:
                kwargs["ResponseGroup"] = args[1]
            else:
                raise RuntimeError("Cannot have keyword ResponseGroup AND " + 
                                   "provide a second argument")
        return _amazon().ItemSearch(**kwargs)
