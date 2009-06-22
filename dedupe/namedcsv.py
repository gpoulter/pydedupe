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


class NamedCSVReaderRowID(NamedCSVReader):
    """Produce named tuples for its records, with text RowID column inserted.
    Use for CSV files that lack an initial ID column.
    
    @ivar reader: Wrapped CSV reader instance from L{csv}
    @ivar RecordType: The namedtuple class for records.
    @ivar rownum: RowID for the next record to be read from L{reader}.
    """
    
    def __init__(self, iterable, dialect='excel', typename='Record', fields=None, rowid="RowID", startfrom=0):
        """Initialise namedtuple reader.
        @param iterable: File-stream or other source of lines 
        @param dialect: Dialect for of the CSV file (see L{csv})
        @param typename: Name for the namedtuple class.
        @param fields: List/string with record fields.  If None, use CSV header.
        @param rowid: Name of the inserted RowID column with the row number
        @param startfrom: Number of first record
        """
        self.reader = csv.reader(iterable, dialect)
        self.rownum = startfrom
        self.RecordType = namedtuple(typename, 
            [rowid] + (fields if fields else self.reader.next()) )
        
    def __iter__(self):
        return self
        
    def next(self):
        try:
            row = [str(self.rownum)] + self.reader.next()
            self.rownum += 1
            return self.RecordType._make(row)
        except TypeError, err:
            raise IOError("%s (row %d): %s" % (str(err), self.rownum, str(row)))
        
    
### Now support progress logging by wrapping the iterator.    
    
def wclines(filename):
    """Use wc to count lines in given filename"""
    import subprocess as sp
    output = sp.Popen(["wc", "-l", filename], stdout=sp.PIPE).communicate()[0]
    return int(output.split()[0])
        
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

def loglinereader(filename, reader, messages=20, log=logging.info):
    """Counts lines being read and print progress messages.
    
    @param filename: Path to the file being read.
    @param reader: Iterator over filename (lines, records)
    @param messages: Number of progress messages to print.
    @param log: Logging function to use.
    """
    lines = wclines(filename)
    from os.path import basename
    return logiterator(max(1, lines//messages), reader,
        basename(filename) + ": read %d out of " + str(lines), log)

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


def read_examples(stream):
    """Read training data from CSV stream (first row contains headings). First
    column is the ID, second column is semicolon-separated list of IDs that
    the row matches, remaining colums are record fields.
    
    @param stream: CSV input stream with the example records.
    
    @return: List of record namedtuples, and map from record ID to adjacent
    record IDs (duplicates). Latter is bi-directional (a in adj[b] iff b in
    adj[a])
    """
    reader = NamedCSVReader(stream, typename="ExampleRecord")
    Record = reader.RecordType
    records = list(reader)
    adjacency = defaultdict(set)
    for record in records:
        # IDs of adjacent records
        currentid = record[0] 
        neighbourids = set(record[1].split(';'))
        neighbourids.discard('')
        adjacency[currentid].update(neighbourids)
        # Put in the backwards adjacency links
        for otherid in neighbourids:
            adjacency[otherid].add(currentid)
    return records, adjacency

