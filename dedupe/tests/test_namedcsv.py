"""Tests of the namedcsv module"""

from os.path import dirname, join
from StringIO import StringIO
import unittest

from dedupe.namedcsv import (
    logiterator, 
    loglinereader, 
    NamedCSVReader, 
    NamedCSVReaderRowID, 
    wclines,
    read_examples,
)

class TestNamedCSV(unittest.TestCase):
    """Reader of CSV files as namedtuples."""
        
    def test_logiterator(self):
        """L{logiterator}"""        
        for x in logiterator(10, xrange(20)):
            pass
        
    def test_wclines(self):
        """L{wclines}"""
        import os, tempfile
        fname = tempfile.mktemp()
        try:
            open(fname,'w').write('a\nb\n')
            self.assertEqual(wclines(fname), 2)
        finally:
            os.remove(fname)

    def test_NamedCSVReader(self):
        """L{NamedCSVReader}"""
        from StringIO import StringIO
        
        reader = NamedCSVReader(StringIO("A,B\na,b\nc,d\n"))
        n = reader.next()
        self.assertEqual(reader.RecordType.__name__, "Record")
        self.assertEqual(n, reader.RecordType('a','b'))
        
    def test_NamedCSVReaderRowID(self):
        """L{NamedCSVReaderRowID}"""
        from StringIO import StringIO
        reader = NamedCSVReaderRowID(StringIO("A,B\na,b\nc,d\n"), startfrom=3)
        n = reader.next()
        self.assertEqual(reader.RecordType.__name__, "Record")
        self.assertEqual(n, reader.RecordType('3', 'a','b'))
    
    def test_read_examples(self):
        """L{read_examples} - Example records and what each matches."""
        stream = StringIO('ID,Matches,Name\n1,2;3,A\n2,1,B\n3,,C\n4,2,D\n')
        examples, adjacency = read_examples(stream)
        self.assertEqual(adjacency, 
            { '1':set(['2','3']), '2':set(['1','4']), 
              '3':set(['1']), '4':set(['2']) })
        
if __name__ == "__main__":
    logsetup.console_logger_only()
    unittest.main()
