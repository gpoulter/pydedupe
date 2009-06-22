"""This module defines two record linkage modes that
combine indexing and comparison into a single operation.  These two
modes are the logical operations "dedupe" (within one dataset) and "link"
(between two data sets).

Each linkage algorithm needs for input L{Indeces} and L{RecordComparator}
objects from the L{indexer} module, and a list or two lists of records.

A "comparison" here refers to a tuple of similarity values in the 0.0-1.0 range,
being the field-by-field similarity of a pair of records, having the type
of the namedtuple L{RecordComparator.Weights}

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

from indexer import Indeces, RecordComparator
import logging

def dedupe(records, indeces, comparator):
    """Dedupe records against itself.
    @param records: Iteration of record namedtuples.
    @param indeces: L{indexer.Indeces}
    @param comparator: L{indexer.RecordComparator}
    @return: comparisons as (rec1,rec2):weights, and indeces as L{Indeces}
    """
    assert isinstance(indeces, Indeces)
    assert isinstance(comparator, RecordComparator)
    indeces.insert(records)
    logging.info("Dedupe index statistics follow...")
    indeces.log_index_stats()
    comparisons = comparator.compare_indexed(indeces)
    return comparisons, indeces


def link(records1, records2, indeces, comparator):
    """Link records1 against records2.
    @param records1, records2: Iterations of record namedtuples.
    @param indeces: L{indexer.Indeces}
    @param comparator: L{indexer.RecordComparator}
    @return: comparisons as (rec1,rec2):weights, and two Indeces instances
    """
    assert isinstance(indeces, Indeces)
    assert isinstance(comparator, RecordComparator)
    import copy
    def index(records):
        myindeces = copy.deepcopy(indeces)
        myindeces.insert(records)
        return myindeces
    indeces1, indeces2 = [ index(records) for records in (records1, records2) ]
    logging.info("Record linkage index statistics follow...")
    indeces1.log_index_stats(indeces2)
    comparisons = comparator.compare_indexed(indeces1, indeces2)
    return comparisons, indeces1, indeces2
