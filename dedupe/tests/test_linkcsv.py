#!/usr/bin/env python

import sys, unittest
from os.path import dirname, join
sys.path.insert(0, dirname(dirname(dirname(__file__))))

def classify(comparisons):
    """Returns match pairs and non-match pairs.
    
    :type comparisons: {(R,R):[float,...]}
    :param comparisons: similarity vectors for pairs of records

    >>> classify({(1,2):[0.8], (2,3):[0.2]})
    ({(1, 2): 1.0}, {(2, 3): 0.0})
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
        
        # fudge the built-in open function for linkcsv
        iostreams = {}
        def fakeopen(f,m):
            from contextlib import closing
            from StringIO import StringIO
            stream = StringIO()
            stream.close = lambda: None
            iostreams[f] = stream
            return closing(stream)
        from dedupe import linkcsv
        linkcsv.open = fakeopen
        import logging
        logging.open = fakeopen
                
        # set up parameters
        from dedupe.sim import ValueSim, RecordSim
        from dedupe.indexer import Index, Indices
        records = [("A","5.5"), ("B","3.5"),("C","5.25")]
        makekey = lambda r: [int(float(r[1]))]
        vcompare = lambda x,y: float(int(x) == int(y))
        indices = Indices(
            ("Idx", Index(makekey)),
        )
        comparator = RecordSim(
            ("Compare", ValueSim(vcompare, 1, float)),
        )

        # do the linking and print the output
        linkcsv.linkcsv(comparator, indices, classify, records, odir="", master=None)
        for name,s in sorted(iostreams.iteritems()):
            print name, '\n', s.getvalue()            
        
        # do the linking and print output
        linkcsv.linkcsv(comparator, indices, classify, records, odir="", master=records)
        for name,s in sorted(iostreams.iteritems()):
            print name, '\n', s.getvalue()            

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
