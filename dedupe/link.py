"""
:mod:`link` -- Record Linkage
=============================

.. module:: link
   :synopsis: Link within and between sets of records.
.. moduleauthor:: Graham Poulter

"""

def within_allpair(compare, records):
    """Return comparisons for all distinct pairs of records.
    
    :type compare: func(R,R) [float,...]
    :param compare: how to obtain similarity of a pair of records.
    :type records: [R,...]
    :param records: find links within this set of records
    :rtype: {(R,R):[float,...],...}
    :return: similarity vectors for ordered pairs of compared records.
    """
    comparisons = {}
    for i in range(len(records)):
        for j in range(i):
            rec1, rec2 = records[i], records[j]
            pair = tuple(sorted([rec1,rec2]))
            if pair not in comparisons:
                comparisons[pair] = compare(rec1, rec2)
    return comparisons

def between_allpair(compare, records1, records2):
    """Return comparisons for all distinct pairs of records.
    
    :type compare: func(R,R) [float,...]
    :param compare: how to obtain similarity of a pair of records.
    :type records1, records2: [R,...]
    :param records1, records2: find links between these sets of records
    :rtype: {(R1,R2):[float,...],...}
    :return: similarity vectors for corresponding pairs of compared records.
    """
    comparisons = {}
    for i in range(len(records1)):
        for j in range(len(records2)):
            rec1, rec2 = records1[i], records2[j]
            pair = (rec1, rec2)
            if pair not in comparisons:
                comparisons[pair] = compare(rec1, rec2)
    return comparisons

def within_indexed(compare, indices):
    """Return comparisons against self for indexed records.
    
    :type compare: func(R,R) [float,...]
    :param compare: how to obtain similarity of a pair of records.
    :type indices: :class:`Indices`, {str:{obj:[R,...],...},...}
    :param indices: indexed left-hand records
    :rtype: {(R,R):[float,...],...}
    :return: comparison similarity vectors for ordered pairs of compared records.
    """
    comparisons = {} # Map from (record1,record2) to L{Weights}
    for index in indices.itervalues():
        index.link_within(compare, comparisons)
    return comparisons

def between_indexed(compare, indices1, indices2):
    """Return comparisons between two sets of indexed records.

    :type compare: func(R,R) [float,...]
    :param compare: how to obtain similarity of a pair of records.
    :type indices1: :class:`Indices`, {str:{obj:[R,...],...},...}
    :param indices1: indexed left-hand records
    :type indices2: :class:`Indices`, {str:{obj:[R,...],...},...}
    :param indices2: indexed right-hand records
    :rtype: {(R,R):[float,...],...}
    :return: similarity vectors for corresponding pairs of compared records.
    """
    if indices1 is indices2:
        raise ValueError("indices1 and indeces2 are the same object.")
    comparisons = {}
    for index1, index2 in zip(indices1.itervalues(), indices2.itervalues()):
        index1.link_between(compare, index2, comparisons)
    return comparisons

def within(compare, indices, records):
    """Find similar pairs within a set of records.
    
    :type compare: func(R,R) [float,...]
    :param compare: how to obtain similarity of a pair of records.
    :type indices: :class:`Indices`
    :param indices: prototypical index layout for the records
    :type records: [:class:`namedtuple`,...]
    :param records: records to be linked
    :rtype: {(R,R):[float,...]}, :class:`Indices`
    :return: comparison similarity vectors for ordered pairs of compared\
    records, and a filled :class:`Indices` instance.
    """
    indices = indices.clone()
    indices.insertmany(records)
    comparisons = within_indexed(compare, indices)
    return comparisons, indices

def between(compare, indices, records1, records2):
    """Find similar pairs between two sets of records.
    
    :type compare: func(R,R) [float,...]
    :param compare: how to obtain similarity of a pair of records.
    :type indices: :class:`Indices`
    :param indices: prototypical index layout for the records
    :type records1: [:class:`namedtuple`,...]
    :param records1: left-hand records to link to right-hand
    :type records2: [:class:`namedtuple`,...]
    :param records2: right-hand being linked to
    :rtype: {(R,R):[float,...]}, :class:`Indices`, :class:`Indices`
    :return: similarity vectors for pairwise comparisons, and the\
    filled :class:`Indices` instances for `records1` and `records2`.
    """
    indices1, indices2 = indices.clone(), indices.clone()
    indices1.insertmany(records1)
    indices2.insertmany(records2)
    comparisons = between_indexed(compare, indices1, indices2)
    return comparisons, indices1, indices2
