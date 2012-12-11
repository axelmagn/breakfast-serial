# 3rd party imports
from lxml import etree


class XMLInterface(object):
    """
    Associate a model with XML data.

    XPath attributes are used to generate models with attributes read from XML
    data.

    """
    model = None
    item_root = etree.XPath("/")

    def __init__(self, xml_data):
        self.xml = xml_data
        # translate class attributes to instance attributes if they are xpaths
        for key, value in enumerate(self.__class__.__dict__):
            if isinstance(value, etree.XPath):
                setattr(self, key, value)
            elif isinstance(value, str) or isinstance(value, unicode):
                setattr(self, key, etree.XPath(value))

    def _get_xpath_attrs(self):
        """Return all interface attributes that are XPaths"""
        return {
                attr: getattr(self, attr) for attr in self.__dict__
                if isinstance(getattr(self, attr), etree.XPath)
        }

    def parse_model(self, xml):
        """
        Return an instance of self.model that maps data to model attributes

        """
        out = self.model()
        attrs = self._get_xpath_attrs()
        for key in attrs:
            result = attrs[key](xml)
            if result:
                setattr(out, result[0])
        return out

    def parse_models(self):
        return list(self.__iter__)

    def __iter__(self):
        """
        Iterate through self.xml, yielding populated models

        """
        for item in self.item_root(self.xml):
            yield self.parse_model(item)

    def __getitem__(self, key):
        if not (isinstance(key, str) or isinstance(key, unicode)):
            raise TypeError("key %s is not a string" % key)
        if not hasattr(self, key):
            raise ValueError("%s has no attribute for key %s" % (self, key))
        val = getattr(self, key)
        if not isinstance(val, etree.XPath):
            raise ValueError("attribute %s of %s is not an XPath" % (key,
                                                                     self))
        return val

