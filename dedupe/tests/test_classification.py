#!/usr/bin/env python

import logging, math, unittest

from dedupe.classification import distance, kmeans, nearest

class TestClassification(unittest.TestCase):
    
    def test_distance_L2(self):
        self.assertEqual(distance.L2([2,None],[5,None]), 3)
        self.assertEqual(distance.L2([2,None],[5,1]), 3)
        self.assertEqual(distance.L2([None,None],[1,1]), 0)
        self.assertEqual(distance.L2([2,2],[3,3]), math.sqrt(2))
        self.assertEqual(distance.L2([3,2],[3,2]), 0)
        self.assertEqual(distance.L2([4,3.0,2,3],[4,1.0,3,3]), math.sqrt(5))

    def test_distance_normL2(self):
        self.assertEqual(distance.normL2([2,None],[5,1],[1,1]), 3)
        self.assertEqual(distance.normL2([2,2],[3,3],[1,1]), math.sqrt(2))
        self.assertEqual(distance.normL2([2,2],[3,3],[0.5,1]), math.sqrt(5))
    
    ## Basic tests of the classifiers        
        
    def test_kmeans(self):
        matches, nomatches = kmeans.classify(
            comparisons = {(1,2):[0.5], (2,3):[0.8], (3,4):[0.9], (4,5):[0.0]},
            distance = distance.L2)
        self.assertEqual(set(matches.keys()), set([(1, 2), (2, 3), (3, 4)]))
        self.assertEqual(set(nomatches.keys()), set([(4, 5)]))
        
    def test_nearest(self):
        matches, nomatches = nearest.classify(
            comparisons= {(1,2):[0.5], (2,3):[0.8], (3,4):[0.9], (4,5):[0.0]},
            examples = [ ([0.3],False), ([1.0],True) ],
            distance = distance.L2)
        self.assertEqual(set(matches.keys()), set([(2, 3), (3, 4)]))
        self.assertEqual(set(nomatches.keys()), set([(1, 2), (4, 5)]))
        
    ## Tests that include None values in the similarity vectors
        
    def test_kmeans_nulls(self):
        matches, nomatches = kmeans.classify(
            comparisons= {(1,2):[0.5,None], (2,3):[0.8,0.7], (3,4):[0.9,0.5], (4,5):[0.0,0.5]},
            distance = distance.L2)
        self.assertEqual(set(matches.keys()), set([(1, 2), (2, 3), (3, 4)]))
        self.assertEqual(set(nomatches.keys()), set([(4, 5)]))

    def test_nearest_nulls(self):
        matches, nomatches = nearest.classify(
            comparisons= {(1,2):[0.5,None], (2,3):[0.8,0.7], (3,4):[0.9,0.5], (4,5):[0.0,0.5]},
            examples = [ ([0.3,0.3],False), ([1.0,0.8],True), ([1.0,None],True) ],
            distance = distance.L2)
        self.assertEqual(set(matches.keys()), set([(2, 3), (3, 4)]))
        self.assertEqual(set(nomatches.keys()), set([(1, 2), (4, 5)]))

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.main()

