#!/usr/bin/env python

import logging, unittest, sys	
from os.path import dirname, join
sys.path.insert(0, dirname(dirname(dirname(__file__))))

from dedupe.encoding import (
    combine,
    digits,
    dmetaphone,
    emaildomain, 
    lowstrip, 
    multivalue,
    normspace, 
    nospace, 
    reverse, 
    sorted_words, 
    urldomain, 
    wrap, 
)

class TestEncoding(unittest.TestCase):
    
    def test_normspace(self):
        self.assertEqual(normspace(" a  b  "), "a b")
    
    def test_nospace(self):
        self.assertEqual(nospace(" a  b  "), "ab")

    def test_lowstrip(self):
        self.assertEqual(lowstrip(" A  b  "), "a b")
        
    def test_urldomain(self):
        self.assertEqual(urldomain("http://www.google.com"), "google.com")
        self.assertEqual(urldomain("www.google.com"), "google.com")
        self.assertEqual(urldomain("http://google.com"), "google.com")
        self.assertEqual(urldomain("http://www.google.com/a"), "google.com")
        self.assertEqual(urldomain("http://www.google.com/a/b"), "google.com")
        
    def test_emaildomain(self):
        self.assertEqual(emaildomain("srtar@arst.com"), "arst.com")
        self.assertEqual(emaildomain("abc"), "abc")
        
    def test_wrap(self):
        self.assertEqual(wrap(sorted_words, reverse)("world hello"), "dlrow olleh")
        
    def test_digits(self):
        self.assertEqual(digits("+27 (21) 1234567"), "27211234567")
        
    def test_dmetaphone(self):
        self.assertEqual(dmetaphone("Cape Town"), ("KPTN", None))
        
    def test_combine(self):
        self.assertEqual(combine(0,2)(['A','B','C']), ['A','C'])
    
    def test_multivalue(self):
        self.assertEqual(multivalue(";",0)(['1;2;3']), ['1','2','3'])
        
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.main()