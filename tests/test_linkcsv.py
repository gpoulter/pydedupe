#!/usr/bin/env python

import logging, sys, unittest
from os.path import dirname, join
sys.path.insert(0, dirname(dirname(dirname(__file__))))

from dedupe import block, sim, linkcsv


def classify(comparisons):
    """Returns match pairs and non-match pairs.

    :type comparisons: {(R, R):[float, ...]}
    :param comparisons: similarity vectors for pairs of records

    >>> comparisons = {(1, 2): [0.8], (2, 3): [0.2]}
    >>> classify(comparisons)
    ({(1, 2): 1.0}, {(2, 3): 0.0})
    """
    matches, nomatches = {}, {}
    for pair, sim in comparisons.iteritems():
        if sim[0] > 0.5:
            matches[pair] = 1.0
        else:
            nomatches[pair] = 0.0
    return matches, nomatches


class FakeOpen:

    def __init__(self, name, mode):
        self.name = name

    def write(self, text):
        sys.stdout.write(self.name + ": " + text)
        sys.stdout.flush()

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        pass


class TestLinkCSV(unittest.TestCase):

    def test(self):
        # fudge the built-in open function for linkcsv
        linkcsv.open = FakeOpen
        logging.open = FakeOpen
        # set up parameters
        records = [("A", "5.5"), ("B", "3.5"), ("C", "5.25")]
        makekey = lambda r: [int(float(r[1]))]
        vcompare = lambda x, y: float(int(x) == int(y))
        indexing = [ ("Idx", block.Index, makekey) ]
        comparator = sim.Record(
            ("Compare", sim.Field(vcompare, 1, float)),
        )
        # link and print the output
        linker = linkcsv.LinkCSV("/single", indexing, comparator, classify, records)
        linker.write_all()
        # link against master and print the output
        linker = linkcsv.LinkCSV("/master", indexing, comparator, classify, records, master=records)
        linker.write_all()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
