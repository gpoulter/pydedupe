#!/usr/bin/env python

import logging, unittest

from dedupe.encoding import (
    digits,
    dmetaphone,
    emaildomain, 
    lowstrip, 
    nospace, 
    reverse, 
    sorted_words, 
    strip, 
    urldomain, 
    wrap, 
)

class TestEncoding(unittest.TestCase):
    
    def test_strip(self):
        self.assertEqual(strip(" a  b  "), "a b")
    
    def test_lowstrip(self):
        self.assertEqual(lowstrip(" A  b  "), "a b")
        
    def test_nospace(self):
        self.assertEqual(nospace(" a  b  "), "ab")
        
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

        
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.main()