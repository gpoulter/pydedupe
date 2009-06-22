#!/usr/bin/python
"""Tests of the text L{encoders} module"""

import unittest

from dedupe.encoders import (
    strip, 
    lowstrip, 
    nospace, 
    urldomain, 
    emaildomain, 
    wrap, 
    sorted_words, 
    reverse, 
    digits,
)

class TestEncoders(unittest.TestCase):
    """L{encoders} module functions"""
    
    def test_value_encode(self):
        """L{strip}, L{lowstrip}, L{nospace}, L{urldomain}, L{wrap}, 
        L{reverse}, L{std}, L{sorted_words}"""
        nil = lambda x:x
        self.assertEqual(strip(" a  b  "), "a b")
        self.assertEqual(lowstrip(" A  b  "), "a b")
        self.assertEqual(nospace(" a  b  "), "ab")
        self.assertEqual(urldomain("http://www.google.com"), "google.com")
        self.assertEqual(urldomain("www.google.com"), "google.com")
        self.assertEqual(urldomain("http://google.com"), "google.com")
        self.assertEqual(urldomain("http://www.google.com/a"), "google.com")
        self.assertEqual(urldomain("http://www.google.com/a/b"), "google.com")
        self.assertEqual(emaildomain("srtar@arst.com"), "arst.com")
        self.assertEqual(emaildomain("abc"), "abc")
        self.assertEqual(wrap(sorted_words, reverse)("world hello"), "dlrow olleh")
        self.assertEqual(digits("+27 (21) 1234567"), "27211234567")

        
if __name__ == "__main__":
    unittest.main()