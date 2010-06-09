"""
Print stats about index sizes and number of comparisons required
================================================================
 
.. moduleauthor:: Graham Poulter
"""

import logging

def indexstats(index, name):
    """Log statistics about block sizes for `index`, prefixing lines with `name`.
    
    >>> from dedupe import block
    >>> makekey = lambda r: [int(r[1])]
    >>> idx = block.Index(makekey, [('A',5.5),('B',4.5),('C',5.25)])
    >>> def log(s,*a):
    ...     print s % a
    >>> logging.info = log
    >>> indexstats(idx, "NumIdx")
    NumIdx: Records=3, Blocks=2, Largest Block=2, Avg Per Block=1.50.
    """
    if not index:
        logging.warn("%s: index is empty." % name)
    else:
        records = sum(len(recs) for recs in index.itervalues())
        largest = max(len(recs) for recs in index.itervalues())
        blocks = len(index)
        logging.info("%s: Records=%d, Blocks=%d, Largest Block=%d, Avg Per Block=%.2f.",
            name, records, blocks, largest, float(records)/blocks)

def within(indices):
    """Log the expected within-index comparisons."""
    for name, index in indices.iteritems():
        logging.info("Index %s may require up to %d comparisons.", 
                     name, index.count())
        indexstats(index, name)

def between(indices1, indices2):
    """Log the expected between-index comparisons."""
    if indices2 is not None:
        for (n1, i1), (n2, i2) in zip(indices1.items(), indices2.items()): 
            logging.info("Index %s to %s may require up to %d comparisons.",
                n1, n2, i1.count(i2))
            indexstats(i1, "Indeces1 " + n1)
            indexstats(i2, "Indeces2 " + n2)
    else:
        within(indices1)


