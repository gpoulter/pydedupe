#!/usr/bin/env python

import logging, unittest
from StringIO import StringIO

from dedupe.namedcsv import logiterator, NamedCSVReader

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

        
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
