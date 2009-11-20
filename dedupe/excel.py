# coding=utf8
"""
:mod:`excel` -- Read and write Excel CSV files with heading rows
================================================================

The default file encoding is Windows cp1252, but any non-null-using encoding
(such as utf-8) may be specified. Text is converted to unicode strings on
reading, and from unicode to native file encoding on writing.

The first row of the files must specify headings for each column, and headings
must be valid Python identifiers for `namedtuple` attributes.  For files
with no heading, a 'fields' parameter is used to construct the namedtuple.

.. moduleauthor:: Graham Poulter
"""

from __future__ import with_statement

import csv
from compat import namedtuple

class reader:
    """An Excel CSV reader (for CP1252 encoding by default) that parses a
    file-like iteration of byte-strings and yields namedtuples where the
    field strings have been decoded to unicode.
    
    :ivar Row: class of the returned rows
    :type Row: namedtuple 
    
    >>> from StringIO import StringIO
    >>> infile = StringIO("\\n".join(["A,B","a,b\xc3\xa9","c,d"]))
    >>> reader = reader(infile, encoding='utf-8')
    >>> reader.next()
    Row(A=u'a', B=u'b\\xe9')
    """
    
    def __init__(self, iterable, dialect=csv.excel, encoding='cp1252', 
                 typename='Row', fields=None):
        """Initialise namedtuple reader.
        :param iterable: File or other iteration of byte-string lines.
        :param dialect: Dialect of the CSV file (see csv module)
        :param typename: Name for the created namedtuple class.
        :param fields: namedtuple of fields, or None to use the CSV header line.
        """
        if isinstance(iterable, basestring):
            iterable = open(iterable) 
        self.encoding = encoding
        self.reader = csv.reader(iterable, dialect)
        self.Row = namedtuple(typename, fields if fields else self.reader.next())
        
    def __iter__(self):
        return self
        
    def next(self):
        try:
            row = [unicode(s, self.encoding) for s in self.reader.next()]
            return self.Row._make(row)
        except TypeError, err:
            raise IOError(str(err) + ": " + str(row))


class writer:
    """An Excel CSV writer which accepts rows of unicode strings and encodes
    them before writing encoded to the output stream. Do not specify encodings
    that use nulls (such as utf-16).
    
    >>> from StringIO import StringIO
    >>> out = StringIO()
    >>> writer = writer(out, encoding='utf-8')
    >>> writer.writerow([u"a",u"b\\xe9"]) # unicode é
    >>> out.getvalue() # utf-8 é
    'a,b\\xc3\\xa9\\r\\n'
    """

    def __init__(self, stream, dialect=csv.excel, encoding='cp1252', **kwds):
        self.encoding = encoding
        self.writer = csv.writer(stream, dialect=dialect, **kwds)

    def writerow(self, row):
        self.writer.writerow([s.encode(self.encoding) for s in row])

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
