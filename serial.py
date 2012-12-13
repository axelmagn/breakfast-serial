# 3rd party imports
from lxml import etree
from bottlenose import Amazon
# local imports
from bserial.models import Book
from bserial.settings import (AMAZON_ACCESS_KEY_ID, AMAZON_SECRET_KEY,
                               AMAZON_ASSOC_TAG)

_REMOVE_NS_XSLT = """
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" indent="no"/>

<xsl:template match="/|comment()|processing-instruction()">
    <xsl:copy>
      <xsl:apply-templates/>
    </xsl:copy>
</xsl:template>

<xsl:template match="*">
    <xsl:element name="{local-name()}">
      <xsl:apply-templates select="@*|node()"/>
    </xsl:element>
</xsl:template>

<xsl:template match="@*">
    <xsl:attribute name="{local-name()}">
      <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:template>
</xsl:stylesheet>
"""

def _amazon():
    return Amazon(AMAZON_ACCESS_KEY_ID, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)

class XMLInterface(object):
    """
    Associate a model with XML data.

    XPath attributes are used to generate models with attributes read from XML
    data.

    """
    model = None
    item_root = etree.XPath("/*")
    _remove_ns_transform = etree.XSLT(etree.fromstring(_REMOVE_NS_XSLT))

    def __init__(self, *args, **kwargs):
        # translate class attributes to instance attributes if they are xpaths
        if args:
            self.xml = args[0]
        for key in self.__class__.__dict__:
            if not key.startswith('_'):
                value = self.__class__.__dict__[key]
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
                setattr(out, key, result[0].text)
        return out

    def parse_models(self):
        return list(self.__iter__())

    def tostring(self):
        return etree.tostring(self.xml, pretty_print=True)

    def __iter__(self):
        """
        Iterate through self.xml, yielding populated models

        """
        for item in self.item_root(self.xml):
            yield self.parse_model(item)
    
    def __getitem__(self, k):
        return self.parse_models()[k]


class AmazonBookInterface(XMLInterface):
    """
    Amazon Book interface that uses bottlenose to query amazon product api

    """
    model = Book
    item_root   =   etree.XPath("Items/Item")
    asin        =   "ASIN"
    title       =   "ItemAttributes/Title"
    author      =   "ItemAttributes/Author"

    def __init__(self,  *args, **kwargs):
        super(AmazonBookInterface, self).__init__()
        method = kwargs.pop('method', 'lookup').lower()
        if method == 'lookup':
            self.xml = _amazon().ItemLookup(**kwargs)
        elif method == 'search':
            self.xml = _amazon().ItemSearch(**kwargs)
        # convert string to XML, stripping namespaces
        self.xml = self._remove_ns_transform(etree.fromstring(self.xml))

