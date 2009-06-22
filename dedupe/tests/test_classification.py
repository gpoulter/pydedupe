#!/usr/bin/python
"""L{util} module tests"""

import math, unittest
from StringIO import StringIO

from dedupe.classification import (
    distL2,
    dist_norm_L2,
    classify_kmeans,
    classify_nearest,
)

class TestClassification(unittest.TestCase):
    """L{util} module functions"""
    
    def test_distL2(self):
        """L{distL2} - Euclidian distance"""
        self.assertEqual(distL2([2,2],[3,3]), math.sqrt(2))
        self.assertEqual(distL2([3,2],[3,2]), 0)
        self.assertEqual(distL2([4,3.0,2,3],[4,1.0,3,3]), math.sqrt(5))

    def test_dist_norm_L2(self):
        """L{dist_norm_L2} - Euclidian distance"""
        self.assertEqual(dist_norm_L2([2,2],[3,3],[1,1]), math.sqrt(2))
        self.assertEqual(dist_norm_L2([2,2],[3,3],[0.5,1]), math.sqrt(5))
    
    def test_classify_kmeans(self):
        """L{classify_kmeans} - K-Means classification"""
        pass
        
    def test_classify_nearest(self):
        """L{classify_nearest} - Nearest neighbour classification"""
        pass
        
if __name__ == "__main__":
    unittest.main()

