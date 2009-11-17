#!/usr/bin/env python

import copy, logging, sys, os, unittest
from os.path import dirname, join
sys.path.insert(0, dirname(dirname(dirname(__file__))))

from dedupe.encoding import digits, lowstrip
from dedupe.compat import namedtuple
from dedupe.sim import RecordSim, ValueSim, ValueSimAvg, ValueSimMax
from dedupe import link
from dedupe.indexer import Index, Indices
        
class TestIndex(unittest.TestCase):
    """L{indexer} module classes."""
    
    def setUp(self):
        self.indices = Indices(
            ('PhoneIdx', Index(lambda x: [x.Name[:2] + "^" + x.Phone[:2]])),
            ('RevNameIdx', Index(lambda x: [x.Name[::-1]])),
        )
    
        self.Record = namedtuple('Record', 'Name Phone')

        # Work with first record only, except for RecordSim tests
        self.recs = [ 
            self.Record('ABCD EFG', '123;456'), #0
            self.Record('ABCD HIJ', '456;234'), #1
            self.Record('ABCD KLM', '789'), #2
            self.Record('ABCD KLS', ''), #3 Has empty phone value
        ]

        # Indexing Result
        self.indices_out = copy.deepcopy(self.indices)
        self.indices_out['PhoneIdx']['AB^12'] = [self.recs[0]]
        self.indices_out['RevNameIdx']['GFE DCBA'] = [self.recs[0]]

        self.namecompare = ValueSim(
            comparevalues = lambda a,b:0.5, 
            field1 = "Name", 
            encode1 = lowstrip, 
            field2 = lambda r:r.Name)
        
        self.phonecompare = ValueSimAvg(
            comparevalues = lambda a,b:0.5, 
            field1 = lambda r: set(r.Phone.split(";")),
            encode1 = digits)
        
        self.phonecomparemax = ValueSimMax(
            comparevalues = lambda a,b:0.5, 
            field1 = lambda r: set(r.Phone.split(";")),
            encode1 = digits)

        # Record comparison definition
        self.comparator = RecordSim(
            ("NameComp", self.namecompare),
            ("PhoneComp", self.phonecompare),
        )

    def test_Index(self):
        indices = copy.deepcopy(self.indices)
        isinstance(indices, Indices)
        
        self.assertEqual(indices['PhoneIdx'].makekey(self.recs[0]), ['AB^12'])
        self.assertEqual(indices['RevNameIdx'].makekey(self.recs[0]), ['GFE DCBA'])

        # Index the first record
        indices.insert(self.recs[:1]) 
        self.assertEqual(indices, self.indices_out) 
        
    def test_link_allpairs(self):
        self.assertEqual(self.comparator(self.recs[0], self.recs[1]),
            self.comparator.Weights(0.5,0.5))
        link.within_allpair(self.comparator, self.recs)
        
    def test_link_indexed(self):
        """L{Indices}, L{RecordSim}"""
        indices1 = copy.deepcopy(self.indices)
        indices2 = copy.deepcopy(self.indices)
        indices1.insert(self.recs)
        indices2.insert(self.recs)
        link.within_indexed(self.comparator, indices1)
        link.between_indexed(self.comparator, indices1, indices2)
        
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.main()
