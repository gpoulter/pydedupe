"""
Compare sets of records
=======================
 
.. moduleauthor:: Graham Poulter
"""

def within_allpair(compare, records):
    """Return comparisons for all distinct pairs of records.
    
    :type compare: func(`R`, `R`) [:class:`float`,...]
    :param compare: how to obtain similarity of a pair of records.
    :type records: [`R`,...]
    :param records: find links within this set of records
    :rtype: {(`R`, `R`):[:class:`float`,...],...}
    :return: similarity vectors for ordered pairs of compared records.
    
    >>> from dedupe import compare
    >>> numcomp = lambda x,y: 2**-abs(float(x[1])-float(y[1]))
    >>> compare.within_allpair(numcomp, [('A','1'),('B','2'),('C','3')])
    {(('A', '1'), ('C', '3')): 0.25, (('B', '2'), ('C', '3')): 0.5, (('A', '1'), ('B', '2')): 0.5}
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
    
    :type compare: func(`R`, `R`) [:class:`float`,...]
    :param compare: how to obtain similarity of a pair of records.
    :type records1, records2: [`R`,...]
    :param records1, records2: find links between these sets of records
    :rtype: {(`R`, `R`):[:class:`float`,...],...}
    :return: similarity vectors for corresponding pairs of compared records.

    >>> from dedupe import compare
    >>> numcomp = lambda x,y: 2**-abs(float(x[1])-float(y[1]))
    >>> compare.between_allpair(numcomp, [('A','1')], [('B','2'),('C','3')])
    {(('A', '1'), ('C', '3')): 0.25, (('A', '1'), ('B', '2')): 0.5}
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
    
    :type compare: func(`R`, `R`) [:class:`float`,...]
    :param compare: how to obtain similarity of a pair of records.
    :type indices: :class:`~indexer.Indices`
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

    :type compare: func(`R`, `R`) [:class:`float`,...]
    :param compare: how to obtain similarity of a pair of records.
    :type indices1: :class:`~indexer.Indices`
    :param indices1: indexed left-hand records
    :type indices2: :class:`~indexer.Indices`
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
    
    :type compare: func(`R`, `R`) [:class:`float`,...]
    :param compare: how to obtain similarity of a pair of records.
    :type indices: :class:`~indexer.Indices`
    :param indices: prototypical index layout for the records
    :type records: [:class:`namedtuple`,...]
    :param records: records to be linked
    :rtype: {(R,R):[float,...]}, :class:`~indexer.Indices`
    :return: comparison similarity vectors for ordered pairs of compared\
      records, and a filled :class:`Indices` instance.
    """
    indices = indices.clone(records)
    _stat_indices_within(indices)
    comparisons = within_indexed(compare, indices)
    return comparisons, indices

def between(compare, indices, records1, records2):
    """Find similar pairs between two sets of records.
    
    :type compare: func(`R`, `R`) [:class:`float`,...]
    :param compare: how to obtain similarity of a pair of records.
    :type indices: :class:`~indexer.Indices`
    :param indices: prototypical index layout for the records
    :type records1: [:class:`namedtuple`,...]
    :param records1: left-hand records to link to right-hand
    :type records2: [:class:`namedtuple`,...]
    :param records2: right-hand being linked to
    :rtype: {(R,R):[float,...]}, :class:`~indexer.Indices`, :class:`~indexer.Indices`
    :return: similarity vectors for pairwise comparisons, and the\
      filled :class:`Indices` instances for `records1` and `records2`.
    """
    indices1 = indices.clone(records1)
    indices2 = indices.clone(records2)
    _stat_indices_between(indices1, indices2)
    comparisons = between_indexed(compare, indices1, indices2)
    return comparisons, indices1, indices2

####################
### log indexing estimates for :func:`within` and :func:`between` 

import logging

def _stat_index(index, name):
    """Log block statistics for `index`, prefixing lines with `name`.
    
    >>> from dedupe.indexer import Index
    >>> makekey = lambda r: [int(r[1])]
    >>> idx = Index(makekey, [('A',5.5),('B',4.5),('C',5.25)])
    >>> def log(s,*a):
    ...     print s % a
    >>> logging.info = log
    >>> _stat_index(idx, "NumIdx")
    NumIdx: 3 records, 2 blocks. 2 in largest block, 1.50 per block.
    """
    if not index:
        logging.warn("%s: index is empty." % name)
    else:
        records = sum(len(recs) for recs in index.itervalues())
        largest = max(len(recs) for recs in index.itervalues())
        blocks = len(index)
        logging.info("%s: %d records, %d blocks. %d in largest block, %.2f per block.",
            name, records, blocks, largest, float(records)/blocks)

def _stat_indices_within(indices):
    """Log about expected within-index comparisons."""
    for name, index in indices.iteritems():
        logging.info("Index %s may require up to %d comparisons.", name, 
            index.count_comparisons())
        _stat_index(index, name)

def _stat_indices_between(indices1, indices2):
    """Log about expected between-index comparisons."""
    for (n1, i1), (n2, i2) in zip(indices1.items(), indices2.items()): 
        logging.info("Index %s to %s may require up to %d comparisons.",
            n1, n2, i1.count_comparisons(i2))
        _stat_index(i1, "Input " + n1)
        _stat_index(i2, "Master " + n2)
