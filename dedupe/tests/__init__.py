#!/usr/bin/python
"""Run all the unit tests"""

import logging, os, re, sys, unittest

def suite():
    """Create test suite from the modules in this directory.  First puts the
    parent dedupe package into the sys.path """
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    dedupe_dir = os.path.dirname(tests_dir)
    dedupe_pkg = os.path.dirname(dedupe_dir)
    sys.path.insert(0, dedupe_pkg)
    testmods = [ 'dedupe.tests.' + re.match(r'(.+?)\.py$', f).group(1) 
                 for f in os.listdir(tests_dir)
                 if re.match(r'test_(.+?)\.py$', f) is not None ]
    print "Testing Modules: %s" % ", ".join(testmods)
    return unittest.defaultTestLoader.loadTestsFromNames(testmods)

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    unittest.TextTestRunner(verbosity=2).run(suite())
