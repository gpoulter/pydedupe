#!/usr/bin/env python

import logging, math, unittest

from dedupe.comparison import (
    dameraulevenshtein, DamerauLevenshtein
)

class TestClassification(unittest.TestCase):
    
    def test_dameraulevenshtein(self):
        self.assertEqual(dameraulevenshtein("abcd","abdc"), 1)
        self.assertEqual(dameraulevenshtein("dbca","abcd"), 2)
        
    def test_DamerauLevenshtein(self):
        self.assertEqual(DamerauLevenshtein()("abcd","abcd"), 1.0)
        self.assertEqual(DamerauLevenshtein()("abcd","abdc"), 0.75)
        self.assertEqual(DamerauLevenshtein(0.5)("abcd","abdc"), 0.5)
        self.assertEqual(DamerauLevenshtein(0.5)("abcd","badc"), 0.0)
        
        
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.main()

