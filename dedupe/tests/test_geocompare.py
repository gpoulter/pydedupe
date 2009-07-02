#!/usr/bin/env python

from __future__ import division

import logging, unittest

from dedupe.geocompare import (
    geodistance, 
    make_geo_comparator, 
    handle_missing, 
    transform_linear,
)

class TestGeoCompare(unittest.TestCase):
    
    km_per_degree = 111.21
    
    def test_geodistance(self):
        self.assertAlmostEqual(geodistance((0,0),(1,0)), self.km_per_degree, 2)
        self.assertAlmostEqual(geodistance((0,0),(0,1)), self.km_per_degree, 2)

    def test_handle_missing(self):
        comp = handle_missing(lambda x,y: 1.0)
        self.assertTrue(comp(0,0) is None)
        self.assertTrue(comp(1,0) is None)
        self.assertEqual(comp(1,1), 1.0)
        self.assertTrue(comp("","arst") is None)
        self.assertEqual(comp("arst","arst"), 1.0)
        
    def test_transform_linear(self):
        self.assertAlmostEqual(transform_linear(4, (0,5), (1,0)), 0.2, 2)
        self.assertAlmostEqual(transform_linear(2, (0,1), (1,0)), 0, 2)
        
    def test_make_geo_comparator(self):
        # Set the maximum to be 1.5 degrees (for 0 similarity)
        geo_comparator = make_geo_comparator(self.km_per_degree*1.5)
        # Therefore 1 degree should have 33% similarity, to two decimal places
        self.assertAlmostEqual(geo_comparator((0.0,0.0), (1.0,0.0)), 1/3, 2)
       

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.main()
