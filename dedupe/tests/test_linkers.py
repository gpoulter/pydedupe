#!/usr/bin/env python

import csv, logging, os, shutil, sys, tempfile, unittest

from dedupe.febrl.comparison import FieldComparatorDaLeDist
from dedupe.encoding import lowstrip, dmetaphone
from dedupe.indexer import Index, Indeces, ValueComparator, RecordComparator

from dedupe.linkers import csvdedupe

dale = FieldComparatorDaLeDist(
    agree_weight = 1.0,
    disagree_weight = 0.0,
    missing_values = [None,''],
    missing_weight = 0.2,
    threshold = 0.5).compare

class TestCSVDedupe(unittest.TestCase):
    
    def setUp(self):
        
        self.records = [
            ("Joe Bloggs",),
            ("Jo Bloggs",),
            ("Jimmy Choo",),
        ]
        
        self.indeces = Indeces(
            ("NameIdx", Index(lambda r: dmetaphone(lowstrip(r[0])))),
        )
        
        self.comparator = RecordComparator(
            ("NameCompare", ValueComparator(dale, 0, lowstrip)),
        )
        
        # Write a temporary file with the 
        self.outdir = tempfile.mkdtemp(prefix="test_linkers_")
        self.inpath = os.path.join(self.outdir, "input.csv")
        csvfile = open(self.inpath,'w') 
        writer = csv.writer(csvfile, lineterminator='\n')
        writer.writerow(("Name",))
        writer.writerows(self.records)
        csvfile.close()
        
    def tearDown(self):
        pass
        #shutil.rmtree(self.outdir)
        
    def dummyclassifier(self, comparisons):
        """Takes a map of (rec1,rec2):similarity, and returns a set of (r1,r2)
        for matched pairs, and for non-matched pairs.  Match is judged by
        whether the first value in the similarity vector is greater than 0.5.
    
        E.g. classifier({ (1,2):[0.8], (2,3):[0.2] }) == {(1,2)}, {(2,3)}
        """
        matches, nomatches = set(), set()
        for pair, sim in comparisons.iteritems():
            if sim[0] > 0.5:
                matches.add(pair)
            else:
                nomatches.add(pair)
        return matches, nomatches
                
    def test(self):
        csvdedupe(self.indeces, self.comparator, self.dummyclassifier, 
                  self.inpath, self.outdir)
        
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.main()
