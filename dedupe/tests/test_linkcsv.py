#!/usr/bin/env python

import csv, logging, os, shutil, sys, tempfile, unittest
from functools import partial

from os.path import dirname, join
sys.path.insert(0, dirname(dirname(dirname(__file__))))

from dedupe.sim.dale import compare as dale
from dedupe.encoding import lowstrip
from dedupe.encoding.dmetaphone import encode as dmetaphone
from dedupe.sim import ValueSim
from dedupe.indexer import Index, Indices, RecordSim
from dedupe.linkcsv import csvdedupe
from dedupe import excel

def classify(comparisons):
    """Takes a map of (rec1,rec2):similarity, and returns a set of (r1,r2)
    for matched pairs, and for non-matched pairs.  Match is judged by
    whether the first value in the similarity vector is greater than 0.5.

    E.g. classifier({ (1,2):[0.8], (2,3):[0.2] }) == {(1,2)}, {(2,3)}
    """
    matches, nomatches = {}, {}
    for pair, sim in comparisons.iteritems():
        if sim[0] > 0.5:
            matches[pair] = 1.0
        else:
            nomatches[pair] = 0.0
    return matches, nomatches

class TestCSVDedupe(unittest.TestCase):
    
    def setUp(self):
        
        self.records = [
            ("Joe Bloggs",),
            ("Jo Bloggs",),
            ("Jimmy Choo",),
        ]
        
        self.indices = Indices(
            ("NameIdx", Index(lambda r: dmetaphone(lowstrip(r[0])))),
        )
        
        self.comparator = RecordSim(
            ("NameCompare", ValueSim(partial(dale, 1.0), 0, lowstrip)),
        )
        
        # Write a temporary file with the 
        self.outdir = tempfile.mkdtemp(prefix="test_linkers_")
        self.inpath = os.path.join(self.outdir, "input.csv")
        csvfile = open(self.inpath,'w') 
        writer = excel.writer(csvfile, lineterminator='\n')
        writer.writerow(("Name",))
        writer.writerows(self.records)
        csvfile.close()
        
    def tearDown(self):
        pass
        #shutil.rmtree(self.outdir)
        
                
    def test(self):
        csvdedupe(self.indices, self.comparator, classify, 
                  self.inpath, self.outdir)
        
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.main()
