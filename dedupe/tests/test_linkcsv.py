#!/usr/bin/env python

import csv, logging, sys, unittest
from contextlib import closing
from StringIO import StringIO

from os.path import dirname, join
sys.path.insert(0, dirname(dirname(dirname(__file__))))

from dedupe.sim import ValueSim, RecordSim
from dedupe.indexer import Index, Indices
from dedupe.linkcsv import linkcsv
from dedupe import excel

def classify(comparisons):
    """Takes a map of (rec1,rec2):similarity, and returns a set of (r1,r2)
    for matched pairs, and for non-matched pairs.  Match is judged by
    whether the first value in the similarity vector is greater than 0.5.

    >>> classify({ (1,2):[0.8], (2,3):[0.2] })
    {(1,2)}, {(2,3)}
    """
    matches, nomatches = {}, {}
    for pair, sim in comparisons.iteritems():
        if sim[0] > 0.5:
            matches[pair] = 1.0
        else:
            nomatches[pair] = 0.0
    return matches, nomatches

class TestLinkCSV(unittest.TestCase):
        
    def test(self):
        records = [("A","5.5"), ("B","3.5"),("C","5.25")]
        makekey = lambda r: [int(float(r[1]))]
        vcompare = lambda x,y: float(int(x) == int(y))
        indices = Indices(
            ("NumIdx", Index(makekey)),
        )
        comparator = RecordSim(
            ("NumCompare", ValueSim(vcompare, 1, float)),
        )
        iostreams = {}
        def fakeopen(f,m):
            stream = StringIO()
            stream.close = lambda: None
            iostreams[f] = stream
            return stream
        instream = StringIO()
        writer = excel.writer(instream, lineterminator='\n')
        writer.writerow(("Name","Age"))
        writer.writerows(records)
        instream.seek(0) # start of file
        linkcsv(comparator, indices, classify, instream, 
                odir="", masterstream=None, open=fakeopen,
                logger=logging.getLogger())
        for name,s in iostreams.iteritems():
            print name, '\n', s.getvalue()
        
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.main()
