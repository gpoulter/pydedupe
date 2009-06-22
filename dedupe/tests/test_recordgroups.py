#!/usr/bin/python
"""L{recordgroups} module tests"""

import unittest

from dedupe.recordgroups import (
    adjacency_list, 
    components, 
    tabulate,
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
        ]
        self.recordmap = dict((r[0],r) for r in self.records)
        self.matches = [ [self.recordmap[a], self.recordmap[b]] for a,b in self.matchedids ]
        
    def test_adjacency_list(self):
        """L{adjacency_list}"""
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
        """L{components}"""
        adjlist = adjacency_list(self.matches)
        groups = components(adjlist)
        self.assertEqual(groups, [[('a', 1), ('b', 2), ('c', 3)], 
                                  [('d', 4), ('e', 5), ('f', 6)]])
        
    def test_tabulate(self):
        """L{tabulate}"""
        adjlist = adjacency_list(self.matches)
        groups = components(adjlist)
        table = list(tabulate(groups))
        self.assertEqual(table, 
        [['dup', 'a', 1], ['dup', 'b', 2], ['dup', 'c', 3], ('merged', '', ''), 
         ['dup', 'd', 4], ['dup', 'e', 5], ['dup', 'f', 6], ('merged', '', '')])

        
if __name__ == "__main__":
    unittest.main()
