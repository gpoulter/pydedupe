"""Use breadth-first search to identify components in the match graph,
representing groups of matching records.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

import csv, optparse, os, sys
from itertools import chain

def adjacency_list(nodepairs):
    """Construct adjacency list from edge list provided as pairs of nodes.
    Nodes not listed in the edge list (thus not adjacent to anything) are
    absent from the adjacency list.
    
    @param nodepairs: List of (node1, node2) pairs as edge list.
    
    @return: nodes:[node] adjacency list representing the match graph.
    """
    neighbours = {}
    for node1, node2 in nodepairs:
        neighbours.setdefault(node1, [])
        neighbours.setdefault(node2, [])
        neighbours[node1].append(node2)
        neighbours[node2].append(node1)
    return neighbours


def components(adjlist):
    """Construct of groups as graph components using breadth-first search.
    @param adjlist: adjacency list mapping nodes to list of neighbouring nodes .
    @return:  Groups of nodes [[node1,...]...] 
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


def tabulate(groups):
    """Table of groups of related records as iteration over row-tuples.
    @param groups: Iteration over groups of items.
    @return: Iteration over table row tuples.
    """
    if not groups: return # Nothing to tabulate
    # "blank" row for merged records
    blankrecord = ('merged',) + ('',) * len(groups[0][0])
    for group in groups:
        for item in group:
            yield ['dup'] + list(item)
        yield blankrecord


def writegroups(matches, records, fields, singlet_stream, group_stream):
    """Generate and output the merge table.

    @param matches: List of pairs of matching records.
    @param records: Set of all records.
    @param fields: List of CSV headings for the records.
    @param singlet_stream: Write CSV rows for single (unique) records here
    @param group_stream: Write CSV groups for groups of dup records here

    @return: adjlist (map from id to list of ids being duplicates),
             singlets (list of single ids that match nothing else).
             groups (list of groups, each group being a lists of ids),
    """
    adjlist = adjacency_list(matches)
    groups = components(adjlist)
    # Identify singlet records (nothing in the adjacency list)
    singlets = [rec for rec in records if rec not in adjlist]
    csv.writer(singlet_stream, dialect='excel').writerows(
        chain([fields], singlets))
    # Groups of related duplicates with status column (dup/unique/merge)
    csv.writer(group_stream, dialect='excel').writerows(
        chain([('status',)+fields], tabulate(groups)))
    return adjlist, singlets, groups
