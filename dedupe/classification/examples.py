"""Load training records from disk and perform all-pair comparisons to produce
match and non-match similarity vectors for training a supervised classifier of
similarity vectors.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

import csv
from dedupe.indexer import Index, Indeces, RecordComparator
from dedupe.namedcsv import NamedCSVReader

def read_similarities(comparator, inpath, outpath=None):
    """Read groups of records from a file and perform all-pairs comparisons
    within each group, and return the set of all comparison vectors.

    @param comparator: L{RecordComparator} for comparing pairs of records. May
    provide a simple comparison function instead provided that outpath is
    None.

    @param inpath: Path to CSV file, where the first column is the group
    ID for blocking comparisons and the rest of the file has the columns
    needed by the RecordComparator.
    
    @param outpath: Optional path to write a CSV file containing the
    comparison vectors.
    
    @return: Set of comparison vectors for the comparisons within each group
    """
    reader = NamedCSVReader(inpath, typename="Record")
    records = list(reader)
    # Index on the contents of the first column
    index = Index(lambda r: [r[0].strip()]) 
    indeces = Indeces(("Block",index))
    indeces.insert(records)
    # Compare records within index blocks
    comparisons = index.dedupe(comparator)
    if outpath is not None:
        assert isinstance(comparator, RecordComparator)
        comparator.write_comparisons(indeces, indeces, comparisons, None, open(outpath, 'w'))
    return set(comparisons.values())
 