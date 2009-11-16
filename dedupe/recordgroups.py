"""
:mod:`recordgroups` -- Groups of mutually matching records
==========================================================

Use breadth-first search to identify components in the match graph,
representing groups of matching records.

.. module:: recordgroups
   :synopsis: Create a graph from pairwise matches and calculate the mutually matching groups of records.
.. moduleauthor::: Graham Poulter

"""

import optparse, os, sys
from itertools import chain
from collections import defaultdict

import excel

def adjacency_list(nodepairs):
    """Construct adjacency list from edge list provided as pairs of nodes.
    Nodes not listed in the edge list (thus not adjacent to anything) are
    absent from the adjacency list.
    
    :type nodepairs: [(T,T), ...]
    :param nodepairs: Connections between nodes (pairs that match).
    :rtype: {T:[T,...], ...}
    :return: Nodes adjacent to each node in the graph.
    
    >>> edges = [ (1,2), (2,3), (4,5), (1,5) ]
    >>> dict(adjacency_list(edges))
    {1: [2, 5], 2: [1, 3], 3: [2], 4: [5], 5: [4, 1]}
    """
    neighbours = defaultdict(list)
    for node1, node2 in nodepairs:
        neighbours[node1].append(node2)
        neighbours[node2].append(node1)
    return neighbours

def components(adjlist):
    """Construct of groups as graph components using breadth-first search.
    
    :type adjlist: {T:[T,...],...}
    :param adjlist: Nodes adjacent to each node in the graph.
    :rtype: [[T,...],...]
    :return: Connected components as lists of nodes.
    
    >>> edges = [ (1,2), (2,3), (4,5), (5,6) ]
    >>> components(adjacency_list(edges))
    [[1, 2, 3], [4, 5, 6]]
    """
    groups = [] # List of lists describing groups
    visited = set() # Has node been visited?
    # Perform BFS to label groups
    for node in adjlist.iterkeys():
        if node not in visited:
            newgroup = [] # Start the group
            queue = [node] # Initialise queue
            while len(queue) > 0:
                node = queue.pop(0)
                if node not in visited:
                    newgroup.append(node)
                    visited.add(node)
                    queue.extend(adjlist[node])
            newgroup.sort() # group sorted in natural order
            groups.append(newgroup)
    # Return the list of groups
    return groups

def singles_and_groups(matches, allrecords):
    """Given list of matched pairs, and all records, return the groups
    of similar records, and the singlets
    
    :type matches: [(T,T),...]
    :param matches: Matching pairs of records.
    :type allrecords: :class:`Iterable` [T,...]
    :param allrecords: All records (with and without matches)
    :rtype: [T,...],[[T,...],...]
    :return: single records (match nothing) and groups (of matching records)
    
    >>> singles_and_groups([(1,2),(2,3),(4,5)],[1,2,3,4,5,6,7])
    ([6, 7], [[1, 2, 3], [4, 5]])
    """
    adjlist = adjacency_list(matches) # Map from record to neighbours
    groups = components(adjlist) # List of lists of records
    singles = [rec for rec in allrecords if rec not in adjlist]
    return singles, groups

def write_csv(matches, records, fields, out):
    """Write out the records, with grouping 

    :type matches: :class:`Sequence` [(T,T),...]
    :param matches: List of pairs of matching records.
    :type records: :class:`Iterable` [T,...]
    :param records: Iteration over records.
    :type fields: :class:`Sequence` [:class:`str`,...]
    :param fields: List of CSV headings for the records.
    :type out: writeable
    :param out: Output stream for CSV rowd
    :rtype: [T,...], [[T,...],...]
    :return: list of single rows (no matches) and groups (mutually matching)
    """
    singles, groups = singles_and_groups(matches, records)
    w = excel.writer(out, dialect='excel') 
    w.writerow(["GroupID"] + list(fields))
    # Write groups of similar records
    for groupid, group in enumerate(groups):
        for row in group:
            w.writerow((str(groupid),) + row)
    # Write single records
    for row in singles:
        w.writerow(("-",) + row)
    return singles, groups

