#!/usr/bin/python
"""Run all the unit tests"""

import sys, re, os, unittest

def suite():
    """Create test suite by listing the modules in this directory"""
    testmods = [ 'dedupe.tests.' + re.match(r'(.+?)\.py$', f).group(1) 
                 for f in os.listdir(os.path.dirname(os.path.abspath(__file__)))
                 if re.match(r'test_(.+?)\.py$', f) is not None ]
    print "Testing Modules: %s" % ", ".join(testmods)
    return unittest.defaultTestLoader.loadTestsFromNames(testmods)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
