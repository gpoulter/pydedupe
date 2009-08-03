"""Use breadth-first search to identify components in the match graph,
representing groups of matching records.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

import csv, optparse, os, sys
from itertools import chain
from collections import defaultdict

def adjacency_list(nodepairs):
    """Construct adjacency list from edge list provided as pairs of nodes.
    Nodes not listed in the edge list (thus not adjacent to anything) are
    absent from the adjacency list.
    
    @param nodepairs: List of (node1, node2) pairs as edge list.
    
    @return: nodes:[node] adjacency list representing the match graph.
    """
    neighbours = defaultdict(list)
    for node1, node2 in nodepairs:
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


def singles_and_groups(matches, allrecords):
    """Given list of matched pairs, and all records, return the groups
    of similar records, and the singlets
    
    @param matches: List of (rec1,rec2) matching record pairs
    @param records: Iteration over all records.
    
    @return: singles (list of single ids that match nothing else), and
    groups (list of groups, each group being a lists of ids),
    """
    adjlist = adjacency_list(matches) # Map from record to neighbours
    groups = components(adjlist) # List of lists of records
    singles = [rec for rec in allrecords if rec not in adjlist]
    return singles, groups
    

def writegroups(matches, records, fields, output_stream):
    """Write out the records, with grouping 

    @param matches: List of pairs of matching records.
    @param records: Iteration over records.
    @param fields: List of CSV headings for the records.
    @param output: Output stream for CSV rowd

    @return: singles (list of single ids that match nothing else), and
    groups (list of groups, each group being a lists of ids),
    """
    
    singles, groups = singles_and_groups(matches, records)
    out = csv.writer(output_stream, dialect='excel') 
    out.writerow(["GroupID"] + list(fields))
    # Write groups of similar records
    for groupid, group in enumerate(groups):
        for row in group:
            out.writerow((str(groupid),) + row)
    # Write single records
    for row in singles:
        out.writerow(("-",) + row)
    return singles, groups

