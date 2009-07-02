#!/usr/bin/env python

import logging, math, unittest

from dedupe.comparison import (
    dameraulevenshtein, DamerauLevenshtein,
    levenshtein, Levenshtein,
)

class TestComparison(unittest.TestCase):
    
    def test_dameraulevenshtein(self):
        self.assertEqual(dameraulevenshtein("abcd","ab"), 2)
        self.assertEqual(dameraulevenshtein("abcd","abdc"), 1)
        self.assertEqual(dameraulevenshtein("dbca","abcd"), 2)
        
    def test_DamerauLevenshtein(self):
        self.assertEqual(DamerauLevenshtein()("abcd","abcd"), 1.0)
        self.assertEqual(DamerauLevenshtein()("abcd","abdc"), 0.75)
        self.assertEqual(DamerauLevenshtein(0.5)("abcd","abdc"), 0.5)
        self.assertEqual(DamerauLevenshtein(0.5)("abcd","badc"), 0.0)
        
    def test_levenshtein(self):
        self.assertEqual(levenshtein("abcd","ab"), 2)
        self.assertEqual(levenshtein("abcd","abdc"), 2)
        self.assertEqual(levenshtein("dbca","abcd"), 2)
        
    def test_Levenshtein(self):
        self.assertEqual(Levenshtein()("abcd","abcd"), 1.0)
        self.assertEqual(Levenshtein()("abcd","abdc"), 0.5)
        self.assertEqual(Levenshtein(0.5)("abcd","abdc"), 0.0)
        self.assertEqual(Levenshtein(0.5)("abcd","badc"), 0.0)
        
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.main()

