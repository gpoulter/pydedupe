#!/usr/bin/env python

import logging, math, unittest

from dedupe.classification import (
    distL2,
    dist_norm_L2,
    kmeans_febrl,
    nearest_neighbour,
)

class TestClassification(unittest.TestCase):
    
    def test_distL2(self):
        self.assertEqual(distL2([2,None],[5,None]), 3)
        self.assertEqual(distL2([2,None],[5,1]), 3)
        self.assertEqual(distL2([None,None],[1,1]), 0)
        self.assertEqual(distL2([2,2],[3,3]), math.sqrt(2))
        self.assertEqual(distL2([3,2],[3,2]), 0)
        self.assertEqual(distL2([4,3.0,2,3],[4,1.0,3,3]), math.sqrt(5))

    def test_dist_norm_L2(self):
        self.assertEqual(dist_norm_L2([2,None],[5,1],[1,1]), 3)
        self.assertEqual(dist_norm_L2([2,2],[3,3],[1,1]), math.sqrt(2))
        self.assertEqual(dist_norm_L2([2,2],[3,3],[0.5,1]), math.sqrt(5))
    
    def test_classify_kmeans_febrl(self):
        matches, nomatches = kmeans_febrl(
            comparisons = {(1,2):[0.5], (2,3):[0.8], (3,4):[0.9], (4,5):[0.0]},
            distance = distL2)
        self.assertEqual(matches, set([(1, 2), (2, 3), (3, 4)]))
        self.assertEqual(nomatches, set([(4, 5)]))
        
    def test_classify_nearest_neighbour(self):
        matches, nomatches = nearest_neighbour(
            comparisons= {(1,2):[0.5], (2,3):[0.8], (3,4):[0.9], (4,5):[0.0]},
            examples = [ ([0.3],False), ([1.0],True) ],
            distance = distL2)
        self.assertEqual(matches, set([(2, 3), (3, 4)]))
        self.assertEqual(nomatches, set([(1, 2), (4, 5)]))
        
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.main()

