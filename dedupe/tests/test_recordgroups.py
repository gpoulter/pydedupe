#!/usr/bin/python
"""L{recordgroups} module tests"""

import unittest

from dedupe.recordgroups import (
    adjacency_list, 
    components, 
    singles_and_groups,
    writegroups,
)

class TestGrouping(unittest.TestCase):
    """L{recordgroups} module functions"""
    
    def setUp(self):
        self.matchedids = [
            ["a","b"],
            ["b","c"],
            ["d","e"],
            ["e","f"],
        ]
        self.records = [
            ("a",1),
            ("b",2),
            ("c",3),
            ("d",4),
            ("e",5),
            ("f",6),
            ("g",7),
        ]
        self.recordmap = dict((r[0],r) for r in self.records)
        self.matches = [ [self.recordmap[a], self.recordmap[b]] for a,b in self.matchedids ]
        
    def test_adjacency_list(self):
        adjlist = adjacency_list(self.matches)
        self.assertEqual(adjlist,{
            ('a', 1): [('b', 2)], 
            ('b', 2): [('a', 1), ('c', 3)], 
            ('c', 3): [('b', 2)],
            ('d', 4): [('e', 5)], 
            ('e', 5): [('d', 4), ('f', 6)], 
            ('f', 6): [('e', 5)],
         })
        
        
    def test_components(self):
        adjlist = adjacency_list(self.matches)
        groups = components(adjlist)
        self.assertEqual(groups, [[('a', 1), ('b', 2), ('c', 3)], 
                                  [('d', 4), ('e', 5), ('f', 6)]])
        
    def test_singles_and_groups(self):
        singles, groups = singles_and_groups(self.matches, self.records)
        self.assertEqual(singles, [('g',7)])
        self.assertEqual(groups,  [[('a', 1), ('b', 2), ('c', 3)], 
                                  [('d', 4), ('e', 5), ('f', 6)]])
        
    def test_writegroups(self):
        pass # TODO
        
if __name__ == "__main__":
    unittest.main()
