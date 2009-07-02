"""Tests of the namedcsv module"""

import logging, unittest
from os.path import dirname, join
from StringIO import StringIO

from dedupe.namedcsv import (
    logiterator, 
    NamedCSVReader, 
    read_examples,
)

class TestNamedCSV(unittest.TestCase):
    """Reader of CSV files as namedtuples."""
        
    def test_logiterator(self):
        for x in logiterator(10, xrange(20)):
            pass
        
    def test_NamedCSVReader(self):
        from StringIO import StringIO
        reader = NamedCSVReader(StringIO("A,B\na,b\nc,d\n"))
        n = reader.next()
        self.assertEqual(reader.RecordType.__name__, "Record")
        self.assertEqual(n, reader.RecordType('a','b'))
        
    def test_read_examples(self):
        stream = StringIO('ID,Matches,Name\n1,2;3,A\n2,1,B\n3,,C\n4,2,D\n')
        examples, adjacency = read_examples(stream)
        self.assertEqual(adjacency, 
            { '1':set(['2','3']), '2':set(['1','4']), 
              '3':set(['1']), '4':set(['2']) })
        
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.main()
