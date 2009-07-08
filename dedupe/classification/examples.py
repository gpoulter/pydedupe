"""Load training records from disk and perform all-pair comparisons to produce
match and non-match similarity vectors for training a supervised classifier of
similarity vectors.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

from dedupe.indexer import Index, RecordComparator
from dedupe.namedcsv import NamedCSVReader

def read_similarities(comparator, path):
    """Read groups of records from a file and perform all-pairs comparisons
    within each group, and return the set of all comparison vectors.

    @param comparator: L{RecordComparator} for comparing pairs of records.

    @param path: Path to CSV file, where the first column is the group
    ID for blocking comparisons and the rest of the file has the columns
    needed by the RecordComparator.
    
    @return: Set of comparison vectors for the comparisons within each group
    """
    reader = NamedCSVReader(path, typename="Record")
    records = list(reader)
    index = Index(lambda r: r[0].strip())
    for record in records:
        index.insert(record)
    comparisons = index.dedupe(comparator)
    return set(comparisons.values())
 