"""
Convert example pairs into training vectors
===========================================

.. moduleauthor:: Graham Poulter
"""

def load(comparator, records, outdir=None):
    """Use example records to create match and non-match similarity vectors 
    for training a classifier.
    
    The first two fields of each item in `records` contain metadata for the
    examples. The first field must have `TRUE` or `FALSE` to indicate whether
    its part of a match or non-match comparison, and an index key (typically a
    string) in the second field to defining which records get compared. An
    empty string in first column skips the record (usable for spacing or
    comments when reading records from CSV files). Remaining columns are
    record data for the `comparator`.

    :type comparator: function(`R`, `R`) [:class:`float`,...]
    :param comparator: gets similarity vectors for pairs of records.
    :type records: [('TRUE'|'FALSE', `key`, `value`,..),...]
    :param records: training records with match & key metadata in first two fields.
    :type outdir: :class:`str`
    :param outdir: optional debug para to, write comparisons as CSV to\
       :file:`{outdir}/{foo}_true.csv` and :file:`{outdir}/{foo}_false.csv`.
    :rtype: {[:class:`float`,...],...},{[:class:`float`,...],...}
    :return: similarity vectors of the true comparisons and false comparisons.

    >>> from dedupe.classification import examples
    >>> from ..compat import namedtuple
    >>> R = namedtuple('Record', 'Match ID Name Age')
    >>> records = [
    ...  R('TRUE','1','Joe1',8), R('TRUE','1','Joe2',7), R('TRUE','1','Joe3',3),
    ...  R('TRUE','2','Abe1',3), R('TRUE','2','Abe2',5),
    ...  R('FALSE','3','Zip1',9), R('FALSE','3','Zip2',1),
    ...  R('FALSE','4','Nobody',1)]
    >>> from .. import sim 
    >>> numcomp = lambda x,y: 2**-abs(x-y)
    >>> comparator = sim.Record(("V", sim.Field(numcomp, lambda r:r[3], float)))
    >>> from ..excel import _fake_open
    >>> streams = _fake_open(examples) # redirect open to StringIO
    >>> t, f = examples.load(comparator, records, '/tmp')
    >>> sorted(t)
    [Similarity(V=0.03125), Similarity(V=0.0625), Similarity(V=0.25), Similarity(V=0.5)]
    >>> sorted(f)
    [Similarity(V=0.00390625)]
    >>> streams['/tmp/examples_false.csv'].getvalue().split()
    ['Score,Key,V', ',3,9', ',3,1', '0.0,True,0.00390625']
    >>> streams['/tmp/examples_true.csv'].getvalue().split()
    ['Score,Key,V', ',1,8', ',1,3', '1.0,True,0.03125', ',1,7', ',1,3', '1.0,True,0.0625', ',1,8', ',1,7', '1.0,True,0.5', ',2,3', ',2,5', '1.0,True,0.25']
    """
    from .. import block, sim
    t_rows = [r for r in records if r[0] in ['TRUE','T','YES','Y','1',1,True] ]
    f_rows = [r for r in records if r[0] in ['FALSE','F','NO','N','0',0,False] ]
    # Index on second column and self-compare within blocks
    t_indices = sim.Indices([("Key", block.Index, lambda r: [r[1]])],t_rows)
    f_indices = sim.Indices([("Key", block.Index, lambda r: [r[1]])],f_rows)
    t_sims = t_indices["Key"].compare(comparator)
    f_sims = f_indices["Key"].compare(comparator) 
    # a debug dump of comparisons to CSV to output directory
    if outdir: 
        from os.path import join
        from contextlib import nested
        from ..linkcsv import write_comparisons
        with nested(open(join(outdir, "examples_true.csv"), 'wb'),
                    open(join(outdir, "examples_false.csv"), 'wb')) as\
             (o_true,o_false):
            t_scores = dict((p,1.0) for p in t_sims.iterkeys())
            f_scores = dict((p,0.0) for p in f_sims.iterkeys())
            write_comparisons(o_true, comparator, t_sims, t_scores, t_indices)
            write_comparisons(o_false, comparator, f_sims, f_scores, f_indices)
    return t_sims.values(), f_sims.values()
 
