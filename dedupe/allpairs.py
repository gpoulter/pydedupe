"""
Compare all pairs of records
============================
"""

def within(comparator, records):
    """Compute similarity vectors for all pairs of records in a list.  
    
    :type comparator: func(`R`, `R`) [:class:`float`,...]
    :param comparator: takes a pair of records and returns a similarity vector.
    :type records: [`R`,...]
    :param records: list of records to compare against itself.  This list
    is first sorted to ensure R1 < R2 in comparisons.
    :rtype: {(`R`,`R`):(`float`,...)}
    :return: mapping from pairs of records to similarity vectors.  The
    lexicographically smaller record is always the first in the pair.
    
    >>> from dedupe import allpairs
    >>> numcomp = lambda x,y: 2**-abs(float(x[1])-float(y[1]))
    >>> records = [('A','1'),('B','2'),('C','3')]
    >>> allpairs.within(numcomp, records)
    {(('A', '1'), ('C', '3')): 0.25, (('B', '2'), ('C', '3')): 0.5, (('A', '1'), ('B', '2')): 0.5}
    """
    comparisons = {}
    records.sort()
    for i in range(len(records)):
        for j in range(i):
            pair = records[j], records[i]
            if pair not in comparisons:
                comparisons[pair] = comparator(*pair)
    return comparisons

def between(comparator, records1, records2):
    """Compute similarity vectors for all pairs of records in two lists. Each record
    in the first list is compared against each record in the second list.
    
    :type comparator: func(`R`, `R`) [:class:`float`,...]
    :param comparator: takes a pair of records and returns a similarity vector.
    :type records1, records2: [`R`,...]
    :param records1, records2: list of records.
    :rtype: {(`R`,`R`):(`float`,...)}
    :return: mapping from pairs of records to similarity vectors.

    >>> from dedupe import allpairs
    >>> numcomp = lambda x,y: 2**-abs(float(x[1])-float(y[1]))
    >>> recs1 = [('A','1')]
    >>> recs2 = [('B','2'),('C','3')]
    >>> allpairs.between(numcomp, recs1, recs2)
    {(('A', '1'), ('C', '3')): 0.25, (('A', '1'), ('B', '2')): 0.5}
    """
    comparisons = {}
    for i in range(len(records1)):
        for j in range(len(records2)):
            rec1, rec2 = records1[i], records2[j]
            pair = (rec1, rec2)
            if pair not in comparisons:
                comparisons[pair] = comparator(rec1, rec2)
    return comparisons
