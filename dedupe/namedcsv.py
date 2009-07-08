"""Classes for reading CSV files with rows as L{namedtuple} instances.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

from __future__ import with_statement

import csv, os, logging
from compat import namedtuple
from collections import defaultdict


class NamedCSVReader(object):
    """Produces named tuples for its records.
    @ivar reader: Wrapped CSV reader instance from L{csv}
    @ivar RecordType: The namedtuple class for records.    
    """
    
    def __init__(self, iterable, dialect='excel', typename='Record', fields=None):
        """Initialise namedtuple reader.
        @param iterable: File or other source of lines (or path to ASCII file)
        @param dialect: Dialect for of the CSV file (see L{csv})
        @param typename: Name for the namedtuple class.
        @param fields: List/string with record fields.  If None, use CSV header.
        """
        if isinstance(iterable, basestring):
            iterable = open(iterable) 
        self.reader = csv.reader(iterable, dialect)
        self.RecordType = namedtuple(typename, fields if fields else self.reader.next())
        
    def __iter__(self):
        return self
        
    def next(self):
        try:
            row = self.reader.next()
            return self.RecordType._make(row)
        except TypeError, err:
            raise IOError(str(err) + ": " + str(row))


### Now support progress logging by wrapping the iterator.    
    
def logiterator(k, iterator, format='Completed %d items', log=logging.info):
    """Wrap an iterator so that it logs the progress of indexing.
    @param k: Message every k items.
    @param format: Message format string with a %d for the number of records.
    @param log: Logging function to use.
    """
    assert k >= 1
    for idx, item in enumerate(iterator):
        yield item
        if (idx+1) % k == 0:
            log(format % (idx+1))

def makeoutputdir(dirname, open=open):
    """Create a directory and return opener factories for files
    in that directory."""
    if not os.path.exists(dirname): 
        os.mkdir(dirname)
    def outpath(filename):
        """Return path to named output file."""
        return os.path.join(dirname, filename)
    def outfile(filename):
        """Return write-only stream for named output file."""
        return open(outpath(filename), 'w')
    return outpath, outfile


