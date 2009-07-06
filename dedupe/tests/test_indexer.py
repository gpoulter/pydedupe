#!/usr/bin/env python

import copy, logging, sys, os, unittest

from dedupe.encoding import lowstrip, split_field
from dedupe.compat import namedtuple

from dedupe.indexer import (
    Index, 
    Indeces, 
    RecordComparator, 
    ValueComparator, 
    SetComparator
)
        
class TestIndex(unittest.TestCase):
    """L{indexer} module classes."""
    
    def setUp(self):
        self.indeces = Indeces(
            ('PhoneIdx', Index(lambda x: (x.Name[:2] + "^" + x.Phone[:2]))),
            ('RevNameIdx', Index(lambda x: x.Name[::-1])),
        )
    
        self.Record = namedtuple('Record', 'Name Phone')

        # Work with first record only, except for RecordComparator tests
        self.recs = [ 
            self.Record('ABCD EFG', '123;456'), #0
            self.Record('ABCD HIJ', '456;234'), #1
            self.Record('ABCD KLM', '789'), #2
            self.Record('ABCD KLS', ''), #3 Has empty phone value
        ]

        # Indexing Result
        self.indeces_out = copy.deepcopy(self.indeces)
        self.indeces_out['PhoneIdx']['AB^12'] = [self.recs[0]]
        self.indeces_out['RevNameIdx']['GFE DCBA'] = [self.recs[0]]

        self.namecompare = ValueComparator(
            comparevalues = lambda a,b:0.5, 
            field1 = "Name", 
            encode1 = lowstrip, 
            field2 = lambda r:r.Name)
        
        self.phonecompare = SetComparator(
            comparevalues = lambda a,b:0.5, 
            field1 = lambda r: set(r.Phone.split(";")),
            encode1 = lowstrip)
        
        # Record comparison definition
        self.comparator = RecordComparator(
            ("NameComp", self.namecompare),
            ("PhoneComp", self.phonecompare),
        )

    def test_Index(self):
        indeces = copy.deepcopy(self.indeces)
        isinstance(indeces, Indeces)
        
        self.assertEqual(indeces['PhoneIdx'].makekey(self.recs[0]), 'AB^12')
        self.assertEqual(indeces['RevNameIdx'].makekey(self.recs[0]), 'GFE DCBA')

        # Index the first record
        indeces.insert(self.recs[:1]) 
        self.assertEqual(indeces, self.indeces_out) 
        indeces.log_index_stats()
        indeces.log_index_stats(indeces)

        # Don't crash given empty list of comparisons
        self.failureException(self.comparator.write_comparisons(
            indeces, indeces, {}, {}, sys.stdout))
        
    def test_ValueComparator(self):
        self.assertEqual(self.namecompare(self.recs[0], self.recs[1]), 0.5)
    
    def test_SetComparator(self):
        phonecomp = self.phonecompare
        isinstance(phonecomp, SetComparator)
        
        # Returns 0.2 for missing values, otherwise 0.5
        phonecomp.comparevalues = lambda x,y: 0.2 if not (x and y) else 0.5 
        self.assertEqual(phonecomp(self.recs[3], self.recs[3]), 0.2)  # rec[3] has phone missing
        self.assertEqual(phonecomp(self.recs[2], self.recs[1]), 0.5)  # rec[1] and rec[2] have phone

    def test_RecordComparator_compare_all_pairs(self):
        self.assertEqual(self.comparator.compare(self.recs[0], self.recs[1]),
            self.comparator.Weights(0.5,0.5))
        self.comparator.allpairs(self.recs)
        
    def test_RecordComparator_compare_indexed(self):
        """L{Indeces}, L{RecordComparator}"""
        indeces1 = copy.deepcopy(self.indeces)
        indeces2 = copy.deepcopy(self.indeces)
        indeces1.insert(self.recs)
        indeces2.insert(self.recs)
        self.comparator.dedupe(indeces1)
        self.comparator.link(indeces1, indeces2)
        
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.main()
