#!/usr/bin/env python

from __future__ import division

import logging, math, unittest

from dedupe.compat import namedtuple

from dedupe.comparison import (
    dameraulevenshtein, DamerauLevenshtein,
    levenshtein, Levenshtein,
    geofield, is_geo_coordinates, geodistance, GeoDistance,
)

class TestComparison(unittest.TestCase):
    
    def test_dameraulevenshtein(self):
        self.assertEqual(dameraulevenshtein("abcd","ab"), 2)
        self.assertEqual(dameraulevenshtein("abcd","abdc"), 1)
        self.assertEqual(dameraulevenshtein("dbca","abcd"), 2)
        
    def test_DamerauLevenshtein(self):
        self.assertEqual(DamerauLevenshtein()("abcd","abcd"), 1.0)
        self.assertEqual(DamerauLevenshtein()("abcd","abdc"), 0.75)
        self.assertEqual(DamerauLevenshtein()("abcd",""), None)
        self.assertEqual(DamerauLevenshtein(0.5)("abcd","abdc"), 0.5)
        self.assertEqual(DamerauLevenshtein(0.5)("abcd","badc"), 0.0)
        
    def test_levenshtein(self):
        self.assertEqual(levenshtein("abcd","ab"), 2)
        self.assertEqual(levenshtein("abcd","abdc"), 2)
        self.assertEqual(levenshtein("dbca","abcd"), 2)
        
    def test_Levenshtein(self):
        self.assertEqual(Levenshtein()("abcd","abcd"), 1.0)
        self.assertEqual(Levenshtein()("abcd","abdc"), 0.5)
        self.assertEqual(Levenshtein()("abcd",""), None)
        self.assertEqual(Levenshtein(0.5)("abcd","abdc"), 0.0)
        self.assertEqual(Levenshtein(0.5)("abcd","badc"), 0.0)
        
        
class TestGeoDistance(unittest.TestCase):
    
    km_per_degree = 111.21
    
    def test_geofield(self):
        from functools import partial
        getter = partial(geofield, "Lat", "Lon")
        MyTuple = namedtuple("MyTuple", ("Name","Lon","Lat"))
        x = MyTuple("Joe", 10.0, 20.0)
        self.assertEqual(getter(x), (20.0, 10.0))
    
    def test_geodistance(self):
        self.assertAlmostEqual(geodistance((0.0,0.0),(1.0,0.0)), self.km_per_degree, 2)
        self.assertAlmostEqual(geodistance((0.0,0.0),(0.0,1.0)), self.km_per_degree, 2)

    def test_is_geo_coordinats(self):
        self.assertFalse(is_geo_coordinates((0.0,0)))
        self.assertTrue(is_geo_coordinates((0.0,0.0)))
        self.assertTrue(is_geo_coordinates((0.0,90.0)))
        self.assertFalse(is_geo_coordinates((91.0,0.0)))
        self.assertFalse(is_geo_coordinates(None))
        self.assertTrue(is_geo_coordinates((-1.0,-1.0)))
        
    def test_GeoDistance(self):
        # Set the maximum to be 1.5 degrees (for 0 similarity)
        geo = GeoDistance(self.km_per_degree*1.5)
        # Therefore 1 degree should have 33% similarity, to two decimal places
        self.assertAlmostEqual(geo((0.0,0.0), (1.0,0.0)), 1/3, 2)

        
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.main()

