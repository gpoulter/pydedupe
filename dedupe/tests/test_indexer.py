#!/usr/bin/python
"""L{indexer} and L{encoders} module tests"""

import copy, sys, os, unittest

from dedupe.encoders import lowstrip, split_field
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
        self.indeces = copy.deepcopy(self.indeces)
        self.indeces['PhoneIdx']['AB^12'] = set([self.recs[0]])
        self.indeces['RevNameIdx']['GFE DCBA'] = set([self.recs[0]])

        # Record comparison definition
        self.comparator = RecordComparator(
            ("NameComp", ValueComparator(
                comparevalues = lambda a,b:0.5, 
                field1 = "Name", 
                encode1 = lowstrip, 
                field2 = lambda r:r.Name)),
            ("PhoneComp", SetComparator(
                comparevalues = lambda a,b:0.5, 
                field1 = lambda r: set(r.Phone.split(";")),
                encode1 = lowstrip)),
        )

    def test_Index(self):
        """L{Index}"""
        indeces = self.indeces
        self.assertEqual(indeces['PhoneIdx'].makekey(self.recs[0]), 'AB^12')
        self.assertEqual(indeces['RevNameIdx'].makekey(self.recs[0]), 'GFE DCBA')
        indeces.insert(self.recs[:1]) # Index first record only
        # Check indexing of first record
        self.assertEqual(indeces['PhoneIdx'], self.indeces['PhoneIdx']) 
        self.assertEqual(indeces['RevNameIdx'], self.indeces['RevNameIdx']) 
        # Edge case: must not crash given empty list of comparisons
        self.failureException(self.comparator.write_comparisons(
            indeces, indeces, {}, sys.stdout))

    def test_RecordComparator(self):
        """L{RecordComparator}, L{ValueComparator}, L{SetComparator}"""
        self.assertEqual(self.comparator.compare(self.recs[0], self.recs[1]),
            self.comparator.Weights(0.5,0.5))
        self.comparator.compare_all_pairs(self.recs)
        
    def test_SetComparator(self):
        """L{SetComparator} finds average similarity of two sets of values."""
        fc = self.comparator['PhoneComp']
        isinstance(fc, SetComparator)
        # Returns 0.2 for missing values, otherwise 0.5
        fc.comparevalues = lambda x,y: 0.2 if not (x and y) else 0.5 
        self.assertEqual(fc(self.recs[3], self.recs[3]), 0.2)  # rec[3] has phone missing
        self.assertEqual(fc(self.recs[2], self.recs[1]), 0.5)  # rec[1] and rec[2] have phone
        
    def test_Indeces_Comparison(self):
        """L{Indeces}, L{RecordComparator}"""
        indeces1 = copy.deepcopy(self.indeces)
        indeces2 = copy.deepcopy(self.indeces)
        indeces1.insert(self.recs)
        indeces2.insert(self.recs)
        self.comparator.compare_indexed(indeces1)
        self.comparator.compare_indexed(indeces1, indeces2)
        
if __name__ == "__main__":
    console_logger_only()
    unittest.main()
