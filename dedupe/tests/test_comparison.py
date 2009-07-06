#!/usr/bin/env python

from __future__ import division

import logging, math, unittest
from functools import partial

from dedupe.compat import namedtuple

from dedupe.comparison import (
    dameraulevenshtein as dale, 
    levenshtein as edit,
    geo
)

class TestLevenshtein(unittest.TestCase):
    
    def test_dameraulevenshtein_distance(self):
        self.assertEqual(dale.distance("abcd","ab"), 2)
        self.assertEqual(dale.distance("abcd","abdc"), 1)
        self.assertEqual(dale.distance("dbca","abcd"), 2)
        
    def test_dameraulevenshtein_compare(self):
        self.assertEqual(dale.compare(1.0, "abcd","abcd"), 1.0)
        self.assertEqual(dale.compare(1.0, "abcd","abdc"), 0.75)
        self.assertEqual(dale.compare(1.0, "abcd",""), None)
        self.assertEqual(dale.compare(0.5, "abcd","abdc"), 0.5)
        self.assertEqual(dale.compare(0.5, "abcd","badc"), 0.0)
        
        ## Check maxdiffs: should make it less lenient at smaller values
        self.assertAlmostEqual(dale.compare(1.0, "abcdef","abcd"), 2/3)
        self.assertAlmostEqual(dale.compare(0.5, "abcdef","abcd"), 1/3)
        
    def test_levenshtein_distance(self):
        self.assertEqual(edit.distance("abcd","ab"), 2)
        self.assertEqual(edit.distance("abcd","abdc"), 2)
        self.assertEqual(edit.distance("dbca","abcd"), 2)
        
    def test_levenshtein_compare(self):
        self.assertEqual(edit.compare(1.0, "abcd","abcd"), 1.0)
        self.assertEqual(edit.compare(1.0, "abcd","abdc"), 0.5)
        self.assertEqual(edit.compare(1.0, "abcd",""), None)
        self.assertEqual(edit.compare(0.5, "abcd","abdc"), 0.0)
        self.assertEqual(edit.compare(0.5, "abcd","badc"), 0.0)
        
        
class TestGeoDistance(unittest.TestCase):
    
    km_per_degree = 111.21
    
    def test_geo_field(self):
        from functools import partial
        getter = partial(geo.field, "Lat", "Lon")
        MyTuple = namedtuple("MyTuple", ("Name","Lon","Lat"))
        x = MyTuple("Joe", 10.0, 20.0)
        self.assertEqual(getter(x), (20.0, 10.0))
    
    def test_geo_distance(self):
        self.assertAlmostEqual(geo.distance((0.0,0.0),(1.0,0.0)), self.km_per_degree, 2)
        self.assertAlmostEqual(geo.distance((0.0,0.0),(0.0,1.0)), self.km_per_degree, 2)

    def test_geo_valid(self):
        self.assertFalse(geo.valid((0.0,0)))
        self.assertTrue(geo.valid((0.0,0.0)))
        self.assertTrue(geo.valid((0.0,90.0)))
        self.assertFalse(geo.valid((91.0,0.0)))
        self.assertFalse(geo.valid(None))
        self.assertTrue(geo.valid((-1.0,-1.0)))
        
    def test_geo_compare(self):
        # Set the maximum to be 1.5 degrees (for 0 similarity)
        geocompare = partial(geo.compare, self.km_per_degree*1.5)
        # Therefore 1 degree should have 33% similarity, to two decimal places
        self.assertAlmostEqual(geocompare((0.0,0.0), (1.0,0.0)), 1/3, 2)

        
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.main()

