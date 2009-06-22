#!/usr/bin/python
"""L{geocompare} module tests."""

from __future__ import division

import unittest

from dedupe.geocompare import (
    geodistance, 
    make_geo_comparator, 
    handle_missing, 
    transform_linear,
)

class TestDuplicateFlagging(unittest.TestCase):
    """L{util} module functions"""
    
    km_per_degree = 111.21
    
    def test_geodistance(self):
        """Geographical distance calculation"""
        self.assertAlmostEqual(geodistance((0,0),(1,0)), self.km_per_degree, 2)
        self.assertAlmostEqual(geodistance((0,0),(0,1)), self.km_per_degree, 2)

    def test_missing(self):
        """Returning None for missing values"""
        comp = handle_missing(lambda x,y: 1.0)
        self.assertTrue(comp(0,0) is None)
        self.assertTrue(comp(1,0) is None)
        self.assertEqual(comp(1,1), 1.0)
        self.assertTrue(comp("","arst") is None)
        self.assertEqual(comp("arst","arst"), 1.0)
        
    def test_scaling(self):
        """Linearly scaling a value"""
        self.assertAlmostEqual(transform_linear(4, (0,5), (1,0)), 0.2, 2)
        self.assertAlmostEqual(transform_linear(2, (0,1), (1,0)), 0, 2)
        
    def test_geo_similarity(self):
        """Similarity of geographic location."""
        # Set the maximum to be 1.5 degrees (for 0 similarity)
        geo_comparator = make_geo_comparator(self.km_per_degree*1.5)
        # Therefore 1 degree should have 33% similarity, to two decimal places
        self.assertAlmostEqual(geo_comparator((0.0,0.0), (1.0,0.0)), 1/3, 2)
       

if __name__ == "__main__":
    unittest.main()
