"""Classes for reading Excel CSV files with rows as L{namedtuple} instances,
supporting the extended CP1252 characters.

The ureader takes byte string input and returns unicode namedtuples. The
uwriter takes unicode tuples and and writes byte string output. The default
encoding is CP1252, but utf-8 is supported. Null-using encodings like UTF-16
are *not* supported, due to the underlying csv module.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

from __future__ import with_statement

import csv
from compat import namedtuple

class ureader:
    """An Excel CSV reader (for CP1252 encoding by default) that parses a
    file-like iteration of byte-strings and yields namedtuples where the
    field strings have been decoded to unicode. The resulting tuples can be
    written back to file using the L{uwriter} class.
    
    @ivar Row: namedtuple class of the returned rows
    """
    
    def __init__(self, iterable, dialect=csv.excel, encoding='cp1252', typename='Row', fields=None):
        """Initialise namedtuple reader.
        @param iterable: File or other iteration of byte-string lines.
        @param dialect: Dialect of the CSV file (see L{csv})
        @param typename: Name for the created namedtuple class.
        @param fields: namedtuple fields parameter, or None to use the CSV header line.
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


class uwriter:
    """An Excel CSV writer (with CP1252 encoding by default), which takes rows
    of unicode strings and encodes before writing them to the file stream. Do
    not specify encodings that use nulls (such as utf-16)."""

    def __init__(self, stream, dialect=csv.excel, encoding='cp1252', **kwds):
        self.encoding = encoding
        self.writer = csv.writer(stream, dialect=dialect, **kwds)

    def writerow(self, row):
        self.writer.writerow([s.encode(self.encoding) for s in row])

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
