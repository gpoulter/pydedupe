"""
:mod:`classification.examples` - Training similarity vectors
===================================================================

Reads specially formatted CSV file of example pairs tagged as matching
and non-matching pairs.  Performs the comparisons and returns 
two sets fo similarity vectors (match, non-match) 
as training data for classifiers.

.. module:: classification.examples
   :synopsis: Obtain true/false similarity vectors from from CSV example files.
.. moduleauthor:: Graham Poulter
"""

from __future__ import division
from ..indexer import Index, Indeces, RecordComparator
from .. import excel

def load_csv(comparator, inpath, outdir):
    """Load example comparisons from CSV file.
    
    The example CSV file must have column headings for namedtuple loading.
    Rows are only read which have TRUE or FALSE in the first column, and must
    have an index block identifier in the second column. The remaining columns
    must include the headings used by the RecordComparator. with all the
    column names needed by the RecordComparator.

    :type comparator: :class:`dedupe.indexer.RecordComparator`, callable (T,T)
    :param comparator: to obtain similarity vectors from pairs of records.
    :type inpath: path to readable file
    :param inpath: Example CSV file.
    :type outdir: path to writeable directory
    :param outdir: Write comparisons to :file:`{outdir}/{foo}_true.csv` and\
    :file:`{outdir}/{foo}_false.csv`.
    
    :rtype: set([float,...],...), set([float,...],...)
    :return: Sets of similarity vectors for true comparisons and false comparisons.
    """
    from contextlib import nested, closing
    from os.path import basename, join, splitext
    base = splitext(basename(inpath))[0]
    with nested(open(inpath, 'rb'),
        open(join(outdir, base+"_true.csv"), 'wb'),
        open(join(outdir, base+"_false.csv"), 'wb')) as \
        (reader, write_true, write_false):
        load_csv_stream(comparator, reader, write_true, write_false)

   
        
def load_iter(comparator, read_data, write_true, write_false):
    """Load example comparisons from CSV streams.
    
    :param comparator: As for :func:`load_csv`
    :type read_data: readable binary stream
    :type write_true, write_false: writeable binary streams

    >>> from StringIO import StringIO
    >>> data = StringIO('''\\
    ... Match,ID,Name,Age
    ... TRUE,1,Joe1,8
    ... TRUE,1,Joe2,7
    ... TRUE,1,Joe3,3
    ... TRUE,2,Abe1,3
    ... TRUE,2,Abe2,5
    ... FALSE,3,Zip1,9
    ... FALSE,3,Zip2,1
    ... FALSE,4,Nobody,1''')
    >>> compare = lambda a, b: 1.0 - abs(float(a.Age)-float(b.Age))/10
    >>> t, f = load_iter(compare, data, StringIO(), StringIO())
    >>> sorted(t)
    [0.5, 0.59999999999999998, 0.80000000000000004, 0.90000000000000002]
    >>> sorted(f)
    [0.19999999999999996]
    """
    MATCH, BLOCK = 0, 1	
    reader = excel.reader(read_data, typename="Record")
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
    if hasattr(comparator, "write_comparisons"):
        comparator.write_comparisons(t_indeces, t_indeces, t_comparisons, None, write_true)
        comparator.write_comparisons(f_indeces, f_indeces, f_comparisons, None, write_false)
    return t_comparisons.values(), f_comparisons.values()
 