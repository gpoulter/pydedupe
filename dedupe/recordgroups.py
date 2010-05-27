"""
Group matched pairs of records together
=======================================

If A matches B and B matches C, then group A, B and C together.  Use
`func`:write_csv to output original records reorderd to have numbered groups
placed at the top of the files.

.. moduleauthor::: Graham Poulter

"""

import excel

def adjacency_list(nodepairs):
    """Construct adjacency list from edge list provided as pairs of nodes.
    Nodes not listed in the edge list (thus not adjacent to anything) are
    absent from the adjacency list.
    
    :type nodepairs: [(T,T), ...]
    :param nodepairs: connections between nodes (pairs that match).
    :rtype: {T:[T,...], ...}
    :return: nodes adjacent to each node in the graph.
    
    >>> from dedupe import recordgroups
    >>> edges = [ (1,2), (2,3), (4,5), (1,5) ]
    >>> dict(recordgroups.adjacency_list(edges))
    {1: [2, 5], 2: [1, 3], 3: [2], 4: [5], 5: [4, 1]}
    """
    from collections import defaultdict
    neighbours = defaultdict(list)
    for node1, node2 in nodepairs:
        neighbours[node1].append(node2)
        neighbours[node2].append(node1)
    return neighbours

def components(adjlist):
    """Construct of groups as graph components using breadth-first search.
    
    :type adjlist: {T:[T,...],...}
    :param adjlist: nodes adjacent to each node in the graph.
    :rtype: [[T,...],...]
    :return: connected components as lists of nodes.
    
    >>> from dedupe import recordgroups
    >>> edges = [ (1,2), (2,3), (4,5), (5,6) ]
    >>> recordgroups.components(recordgroups.adjacency_list(edges))
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
    :type allrecords: :keyword:`iter` [T,...]
    :param allrecords: All records (with and without matches)
    :rtype: [T,...],[[T,...],...]
    :return: single records (match nothing) and groups (of matching records)
    
    >>> from dedupe import recordgroups
    >>> recordgroups.singles_and_groups([(1,2),(2,3),(4,5)],[1,2,3,4,5,6,7])
    ([6, 7], [[1, 2, 3], [4, 5]])
    """
    adjlist = adjacency_list(matches) # Map from record to neighbours
    groups = components(adjlist) # List of lists of records
    singles = [rec for rec in allrecords if rec not in adjlist]
    return singles, groups

def write_csv(matches, records, ostream, projection):
    """Write out the records, with grouping 

    :type matches: [(T,T),...]
    :param matches: List of pairs of matching records.
    :type records: :keyword:`iter` [T,...]
    :param records: Iteration over records.
    :type ostream: binary writer
    :param ostream: where to write the CSV for the records
    :type projection: :class:`Projection`
    :param projection: Projection from input fields onto output fields.
    :rtype: [T,...], [[T,...],...]
    :return: list of single rows (no matches) and groups (mutually matching)
    """
    singles, groups = singles_and_groups(matches, records)
    w = excel.Writer(ostream, dialect='excel')
    w.writerow(["GroupID"] + list(projection.Row._fields))
    # Write groups of similar records
    for groupid, group in enumerate(groups):
        for row in group:
            w.writerow((str(groupid),) + projection(row))
    # Write single records
    for row in singles:
        w.writerow(("",) + projection(row))
    return singles, groups

