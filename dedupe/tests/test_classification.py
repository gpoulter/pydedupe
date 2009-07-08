#!/usr/bin/env python

from __future__ import division

import csv, logging, math, os, tempfile, unittest

from dedupe.classification import distance, kmeans, nearest, examples

class TestClassifyDistance(unittest.TestCase):
    
    ## Testing the distance functions
    
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


class TestClassifyKmeans(unittest.TestCase):
        
    def test_kmeans(self):
        matches, nomatches = kmeans.classify(
            comparisons = {(1,2):[0.5], (2,3):[0.8], (3,4):[0.9], (4,5):[0.0]},
            distance = distance.L2)
        self.assertEqual(set(matches.keys()), set([(1, 2), (2, 3), (3, 4)]))
        self.assertEqual(set(nomatches.keys()), set([(4, 5)]))
        
    def test_kmeans_nulls(self):
        matches, nomatches = kmeans.classify(
            comparisons= {(1,2):[0.5,None], (2,3):[0.8,0.7], (3,4):[0.9,0.5], (4,5):[0.0,0.5]},
            distance = distance.L2)
        self.assertEqual(set(matches.keys()), set([(1, 2), (2, 3), (3, 4)]))
        self.assertEqual(set(nomatches.keys()), set([(4, 5)]))


class TestClassifyNearest(unittest.TestCase):

    def test_nearest(self):
        matches, nomatches = nearest.classify(
            comparisons= {(1,2):[0.5], (2,3):[0.8], (3,4):[0.9], (4,5):[0.0]},
            ex_matches = [[1.0]],
            ex_nonmatches = [[0.3]],
            distance = distance.L2)
        self.assertEqual(set(matches.keys()), set([(2, 3), (3, 4)]))
        self.assertEqual(set(nomatches.keys()), set([(1, 2), (4, 5)]))
        
    ## Include None values in the similarity vectors
    def test_nearest_nulls(self):
        matches, nomatches = nearest.classify(
            comparisons= {(1,2):[0.5,None], (2,3):[0.8,0.7], (3,4):[0.9,0.5], (4,5):[0.0,0.5]},
            ex_matches = [[1.0,0.8],[1.0,None]],
            ex_nonmatches = [[0.3,0.3]],
            distance = distance.L2)
        self.assertEqual(set(matches.keys()), set([(2, 3), (3, 4)]))
        self.assertEqual(set(nomatches.keys()), set([(1, 2), (4, 5)]))


class TestExamples(unittest.TestCase):
    
    def setUp(self):
        f, self.examplefile = tempfile.mkstemp(prefix="test_examples")
        f = open(self.examplefile, 'w')
        w = csv.writer(f)
        w.writerow(("GroupID", "Name", "Age"))
        w.writerow(("1", "Joe1", "8"))
        w.writerow(("1", "Joe2", "7"))
        w.writerow(("1", "Joe3", "3"))
        w.writerow(("2", "Abe1", "3"))
        w.writerow(("2", "Abe2", "5"))
        w.writerow(("3", "Zip1", "9"))
        f.close()

    def tearDown(self):
        os.remove(self.examplefile)
   
    def test_examples_read_similarities(self):
        def compare(rec1, rec2):
            a, b = int(rec1[2]), int(rec2[2])
            return 1.0 - abs(a-b)/10
        similarities = examples.read_similarities(compare, self.examplefile)
        self.assertEqual(similarities, set([ 5/10,9/10,6/10, 8/10]))


if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.main()

