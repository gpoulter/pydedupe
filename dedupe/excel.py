# coding=utf8
"""
Read and write Excel CSV files with heading rows
================================================

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

def _fake_open(module):
    """Patch module's `open` builtin so that it returns StringIOs instead of
    creating real files, which is useful for testing. Returns a dict that maps
    opened file names to StringIO objects."""
    from contextlib import closing
    from StringIO import StringIO
    streams = {}
    def fakeopen(filename,mode):
        stream = StringIO()
        stream.close = lambda: None
        streams[filename] = stream
        return closing(stream)
    module.open = fakeopen
    return streams

class Reader:
    """An Excel CSV reader (for CP1252 encoding by default) that parses a
    file-like iteration of byte-strings and yields namedtuples where the
    field strings have been decoded to unicode.
    
    :ivar Row: class of the returned rows
    :type Row: namedtuple 
    
    >>> from dedupe import excel
    >>> from StringIO import StringIO
    >>> infile = StringIO("\\n".join(["A,B","a,b\xc3\xa9","c,d"]))
    >>> reader = excel.Reader(infile, encoding='utf-8')
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
        if not fields:
            fields = [ f.strip() for f in self.reader.next() ]
        for field in fields:
            if len(field) == 0:
                raise ValueError("Empty field name")
        from compat import namedtuple
        self.Row = namedtuple(typename, fields)
        
    def __iter__(self):
        return self
        
    def next(self):
        try:
            row = [unicode(s, self.encoding) for s in self.reader.next()]
            return self.Row._make(row)
        except TypeError, err:
            raise IOError(str(err) + ": " + str(row))


class Writer:
    """Excel CSV writer.
    
    Accepts rows of unicode strings and encodes
    them before writing encoded to the output stream. Do not specify encodings
    that use nulls (such as utf-16).
    
    >>> from dedupe import excel
    >>> from StringIO import StringIO
    >>> out = StringIO()
    >>> writer = excel.Writer(out, encoding='utf-8')
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


class Projection:
    """Convert input rows into a consistent output format (column ordering)
    so rows from different schemas can be written to the same CSV
    group file.
    
    :param fields: Ordered list of fields for all projected rows.

    >>> from collections import namedtuple
    >>> A = namedtuple('A', 'a b x y')
    >>> B = namedtuple('B', 'a y c x z')
    >>> a = A(1,2,3,4)
    >>> b = B(1,2,3,4,5)
    >>> P = Projection.unionfields(A._fields, B._fields)
    >>> P(a)
    Row(a=1, b=2, x=3, y=4, c='', z='')
    >>> P(b)
    Row(a=1, b='', x=4, y=2, c=3, z=5)
    """

    def __init__(self, fields):
        from collections import namedtuple
        self.fields = fields
        self.Row = namedtuple('Row', fields)

    @staticmethod
    def unionfields(fields1, fields2):
        """Takes two lists of fields and returns a projection onto
        the list of fields given by fields1 plus any fields from field2 not
        already found in fields1."""
        outfields = list(fields1)
        for field in fields2:
            if field not in outfields:
                outfields.append(field)
        return Projection(outfields)

    def __call__(self, row):
        """Return a row with output columns, given an input row with any
        columns.  Drops any input columns not listed in outfields."""
        return self.Row._make(
            getattr(row, field) if field in row._fields else "" 
                for field in self.fields)

