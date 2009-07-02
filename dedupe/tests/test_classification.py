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
        raise NotImplementedError
        
    def test_classify_nearest_neighbour(self):
        raise NotImplementedError
        
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.main()

