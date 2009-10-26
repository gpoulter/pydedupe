"""Load training records from disk and perform all-pair comparisons to produce
match and non-match similarity vectors for training a supervised classifier of
similarity vectors.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

from ..indexer import Index, Indeces, RecordComparator
from .. import namedcsv

def read_examples(comparator, inpath, outpath=None):
    """Read groups of records from a file and perform all-pairs comparisons
    within each group, and return the set of all comparison vectors.

    @param comparator: L{RecordComparator} to compare pairs of records. If
    outpath outpath is None, a simple comparison function could be used instead.

    @param inpath: Path of CSV example file with headings. The first column is
    the name of the index block. Rows with empty first column are ignored.
    The remaining columns should be titled with all the column names 
    needed by the RecordComparator.
    
    @param outpath: Optional path for writing a CSV file of the
    comparison vectors.
    
    @return: Set of comparison vectors, union of all comparisons made
    within each of the groups.
    """
    MATCH, BLOCK = 0, 1	
    reader = namedcsv.ureader(inpath, typename="Record")
    rows = list(row for row in reader)
    t_rows = [r for r in rows if r[MATCH] == "TRUE"]
    f_rows = [r for r in rows if r[MATCH] == "FALSE"]
    # Index on the contents of the first column
    t_indeces = Indeces(("Block",Index(lambda r: [r[BLOCK].strip()]) ))
    t_indeces.insert(t_rows)
    f_indeces = Indeces(("Block",Index(lambda r: [r[BLOCK].strip()]) ))
    f_indeces.insert(f_rows)
    # Compare records within index blocks
    t_comparisons = t_indeces["Block"].dedupe(comparator)
    f_comparisons = f_indeces["Block"].dedupe(comparator)
    if outpath is not None:
        comparator.write_comparisons(t_indeces, t_indeces, t_comparisons, None, open(outpath+"t", 'w'))
        comparator.write_comparisons(f_indeces, f_indeces, f_comparisons, None, open(outpath+"f", 'w'))
    return set(t_comparisons.values()), set(f_comparisons.values())
 