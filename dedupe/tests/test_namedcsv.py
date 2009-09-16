#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging, sys, unittest
from StringIO import StringIO
from os.path import dirname, join
sys.path.insert(0, dirname(dirname(dirname(__file__))))

from dedupe import namedcsv

class TestNamedCSV(unittest.TestCase):
    """Reader of CSV files as namedtuples."""
        
    def test_ureader(self):
        infile = StringIO("\n".join(["A,B","a,b\xc3\xa9","c,d"]))
        reader = namedcsv.ureader(infile, encoding='utf-8')
        n = reader.next()
        self.assertEqual(reader.Row.__name__, "Row")
        self.assertEqual(n, reader.Row('a',u'bé'))
        
    def test_uwriter(self):
        out = StringIO()
        writer = namedcsv.uwriter(out, encoding='utf-8')
        writer.writerow(["a",u"bé"])
        self.assertEqual(out.getvalue(), "a,b\xc3\xa9\r\n")
        
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
