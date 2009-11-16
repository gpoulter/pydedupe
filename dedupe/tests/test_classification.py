#!/usr/bin/env python

from __future__ import division
import logging, math, os, sys, tempfile, unittest
from os.path import dirname, join
sys.path.insert(0, dirname(dirname(dirname(__file__))))

from dedupe.classification import examples
from dedupe import excel

class TestExamples(unittest.TestCase):
    
    def setUp(self):
        f, self.examplefile = tempfile.mkstemp(prefix="test_examples")
        f = open(self.examplefile, 'w')
        w = excel.writer(f)
        w.writerow(("Match","GroupID", "Name", "Age"))
        w.writerow(("TRUE","1", "Joe1", "8"))
        w.writerow(("TRUE","1", "Joe2", "7"))
        w.writerow(("TRUE","1", "Joe3", "3"))
        w.writerow(("TRUE","2", "Abe1", "3"))
        w.writerow(("TRUE","2", "Abe2", "5"))
        w.writerow(("TRUE","3", "Zip1", "9"))
        f.close()

    def tearDown(self):
        os.remove(self.examplefile)
   
    def test(self):
        def compare(rec1, rec2):
            a, b = int(rec1.Age), int(rec2.Age)
            return 1.0 - abs(a-b)/10
        t_comparisons, f_comparisons = examples.read_examples(compare, self.examplefile)
        self.assertEqual(t_comparisons, set([ 5/10,9/10,6/10, 8/10]))


if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.main()

