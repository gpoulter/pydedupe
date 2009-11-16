#!/usr/bin/env python

import copy, logging, sys, os, unittest
from os.path import dirname, join
sys.path.insert(0, dirname(dirname(dirname(__file__))))

from dedupe.encoding import digits, lowstrip
from dedupe.compat import namedtuple
from dedupe.comparison import Value, AverageValue, MaxValue
from dedupe.indexer import Index, Indeces, RecordComparator
        
class TestIndex(unittest.TestCase):
    """L{indexer} module classes."""
    
    def setUp(self):
        self.indeces = Indeces(
            ('PhoneIdx', Index(lambda x: [x.Name[:2] + "^" + x.Phone[:2]])),
            ('RevNameIdx', Index(lambda x: [x.Name[::-1]])),
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

        self.namecompare = Value(
            comparevalues = lambda a,b:0.5, 
            field1 = "Name", 
            encode1 = lowstrip, 
            field2 = lambda r:r.Name)
        
        self.phonecompare = AverageValue(
            comparevalues = lambda a,b:0.5, 
            field1 = lambda r: set(r.Phone.split(";")),
            encode1 = digits)
        
        self.phonecomparemax = MaxValue(
            comparevalues = lambda a,b:0.5, 
            field1 = lambda r: set(r.Phone.split(";")),
            encode1 = digits)

        # Record comparison definition
        self.comparator = RecordComparator(
            ("NameComp", self.namecompare),
            ("PhoneComp", self.phonecompare),
        )

    def test_Index(self):
        indeces = copy.deepcopy(self.indeces)
        isinstance(indeces, Indeces)
        
        self.assertEqual(indeces['PhoneIdx'].makekey(self.recs[0]), ['AB^12'])
        self.assertEqual(indeces['RevNameIdx'].makekey(self.recs[0]), ['GFE DCBA'])

        # Index the first record
        indeces.insert(self.recs[:1]) 
        self.assertEqual(indeces, self.indeces_out) 
        indeces.log_index_stats()
        indeces.log_index_stats(indeces)

        # Don't crash given empty list of comparisons
        self.failureException(self.comparator.write_comparisons(
            indeces, indeces, {}, {}, sys.stdout))
        
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
