"""
:mod:`linkcsv` -- Record linkage for CSV inputs
===============================================

.. module:: linkcsv
   :synopsis: Link records together from CSV file input.
.. moduleauthor:: Graham Poulter
"""

from StringIO import StringIO
from contextlib import nested, closing
import logging, os
import excel, link, recordgroups 
from indexer import Index, Indices

def write_indices(indices, outdir, prefix):
    """Write indices in CSV format.

    :type indices: :class:`Indices`
    :param indices: write one file per index in this dictionary.
    :type outdir: :class:`str`
    :param outdir: write index files to this directory.
    :type prefix: :class:`str`
    :param prefix: prepend this to each output file name
    
    >>> # fudge the 'open' builtin
    >>> data = StringIO() # the 'file'
    >>> data.close = lambda: None # disable closing
    >>> import linkcsv # patch module
    >>> linkcsv.open = lambda f,m: closing(data)
    >>> # now do the test
    >>> makekey = lambda r: [int(r[1])]
    >>> compare = lambda x,y: float(int(x[1])==int(y[1]))
    >>> indices = Indices(("Idx",Index(makekey, [('A',5.5),('C',5.25)])))
    >>> write_indices(indices, outdir="/tmp", prefix="")
    >>> data.getvalue()
    '5,A,5.5\\r\\n5,C,5.25\\r\\n'
    """
    def write_index(index, stream):
        """Write a single index in CSV format to a stream"""
        writer = excel.writer(stream)
        for indexkey, rows in index.iteritems():
            for row in rows:
                writer.writerow([unicode(indexkey)] + [unicode(v) for v in row])
    from os.path import join
    for indexname, index in indices.iteritems():
        with open(join(outdir, prefix+indexname+'.csv'), 'wb') as stream:
            write_index(index, stream)

def index_stats(index, name, log=None):
    """Log stats about the blocks of `index`, to :class:`Logger`, 
    prefixing lines with `name`.
    
    >>> makekey = lambda r: [int(r[1])]
    >>> idx = Index(makekey, [('A',5.5),('B',4.5),('C',5.25)])
    >>> def log(s,*args):
    ...     print s % args
    >>> index_stats(idx, "NumIdx", log)
    NumIdx: 3 records, 2 blocks. 2 in largest block, 1.50 per block.
    """
    log = log if log else logging.getLogger().info
    if not index:
        log("%s: index is empty." % name)
    else:
        records = sum(len(recs) for recs in index.itervalues())
        largest = max(len(recs) for recs in index.itervalues())
        blocks = len(index)
        log("%s: %d records, %d blocks. %d in largest block, %.2f per block.",
            name, records, blocks, largest, float(records)/blocks)

def stat_indexing_within(indices, log=None):
    """Log about expected within-index comparisons."""
    log = log if log else logging.getLogger().info
    for name, index in indices.iteritems():
        log("Index %s may require up to %d comparisons.", name, 
            index.count_comparisons())
        index_stats(index, name, log)

def stat_indexing_between(indices1, indices2, log=None):
    """Log about expected between-index comparisons."""
    log = log if log else logging.getLogger().info
    for (n1, i1), (n2, i2) in zip(indices1.items(), indices2.items()): 
        log("Index %s to %s may require up to %d comparisons.",
            n1, n2, i1.count_comparisons(i2))
        index_stats(i1, "Input " + n1, log)
        index_stats(i2, "Master " + n2, log)

def write_comparisons(comparator, indices1, indices2, comparisons, scores, 
                      stream, origstream=None):
    """Write pairs of compared records, together with index keys and 
    field comparison weights.  Inspection shows which index keys matched,
    and the field-by-field similarity.
    
    :type comparator: :class:`comp.Record`
    :param comparator: The record comparison instance, including the\
    named field comparison functions.
    
    :type indices1: :class:`Indices`, {str:{obj:[R,...],...},...}
    :param indices1: indexed left-hand records
    :type indices2: :class:`Indices`, {str:{obj:[R,...],...},...}
    :param indices2: indexed right-hand records\
       (provide same object as indices1 for self-linkage)

    :type comparisons: {(R,R):[float,...],...}
    :param comparisons: Similarity vectors from pairs of record comparisons.

    :type scores: {(R,R):float,...} or :keyword:`None`
    :param scores: classifier scores for pairs of records. Omitted in\
    the output if None.
    
    :type stream: binary writer
    :param stream: where to write CSV for similarity vectors.
    
    :type origstream: binary writer
    :param origstream: where to write CSV for pairs of compared original records.
    """
    if not comparisons: return
    from sim import getvalue
    # File for comparison statistics
    writer = excel.writer(stream)
    writer.writerow(["Score"] + indices1.keys() + comparator.keys())
    # File for original records
    record_writer = None
    if origstream is not None:
        record_writer = excel.writer(origstream)
        record_writer.writerow(comparisons.iterkeys().next()[0]._fields)
    # Obtain field-getter for each value comparator
    field1 = [ vcomp.field1 for vcomp in comparator.itervalues() ]
    field2 = [ vcomp.field2 for vcomp in comparator.itervalues() ]
    # Use dummy classifier scores if None were provided
    if scores is None:
        scores = dict((k,0) for k in comparisons.iterkeys())
    # Write similarity vectors to output
    for (rec1, rec2), score in scores.iteritems():
        weights = comparisons[(rec1,rec2)] # look up comparison vector
        keys1 = [ idx.makekey(rec1) for idx in indices1.itervalues() ]
        keys2 = [ idx.makekey(rec2) for idx in indices2.itervalues() ]
        writer.writerow([u""] + 
            [u";".join(unicode(k) for k in kl) for kl in keys1] + 
            [ unicode(getvalue(rec1,f)) for f in field1 ])
        writer.writerow([u""] + 
            [u";".join(unicode(k) for k in kl) for kl in keys2] + 
            [ unicode(getvalue(rec2,f)) for f in field2 ])
        # Tuple of booleans indicating whether index keys are equal
        idxmatch = [ bool(set(k1).intersection(set(k2))) if 
                     (k1 is not None and k2 is not None) else ""
                     for k1,k2 in zip(keys1,keys2) ]
        weightrow = [score] + idxmatch + list(weights)
        writer.writerow(str(x) for x in weightrow)
        if record_writer:
            record_writer.writerow(rec1)
            record_writer.writerow(rec2) 
            
def filelog(path):
    """Set up file logging at `path`."""
    filehandler = logging.FileHandler(path)
    filehandler.setFormatter(
        logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(filehandler)
    return logging.getLogger()

def split_records(matchpairs, records):
    """Divide input records into those that matched the master 
    and those that did not.
    
    :type matchpairs: :class:`Iterable` [(R,R),...] 
    :param matchpairs: pairs of input and master records that matches
    :type records: [R,...]
    :param records: input records
    :rtype: [R,...], [R,...]
    :return: input records that matched, and those that did not match
    
    >>> split_records({(1,100):1.0,(3,300):1.0}, [1,2,3,4])
    ([1, 3], [2, 4])
    """
    matchset = set(a for a,b in matchpairs)
    matchrows = [r for r in records if r in matchset]
    singlerows = [r for r in records if r not in matchset]
    return matchrows, singlerows
    
def writecsv(path, header, rows):
    """Write a `header` and `rows` to a csv file at `path`"""
    with open(path, 'wb') as out:
        writer = excel.writer(out)
        writer.writerow(header)
        writer.writerows(rows)

def linkcsv(comparator, indices, classifier, instream, odir, 
            masterstream=None, logger=None):
    """Run a dedupe task using the specified indices, comparator and classifier.
    
    :type indices: :class:`Indices`
    :param indices: index prototype for the records.
    :type comparator: :class:`RecordSim`, function(R,R) [float,...]
    :param comparator: calculates similarity vectors for record pairs.
    :type classifier: function({(R,R):[float]}) [(R,R)], [(R,R)]
    :param classifier: separate record comparisons into matching and non-matching.
    :type instream: binary reader
    :param instream: where to read CSV of input records
    :type odir: :class:`string`
    :param odir: Directory in which to open output files.
    :type masterstream: binary reader
    :param masterstream: where to read CSV of optional master records,\
       to which the `instream` records should be linked.
    :type logger: :class:`Logger` or :keyword:`None`
    :param logger: Log to write to, else set up :file:`{odir}/dedupe.log`
    """
    opath = lambda f: os.path.join(odir, f)
    logger = logger if logger else filelog(opath('dedupe.log'))

    # Index records, compare pairs, identify match/nonmatch pairs
    records = list(excel.reader(instream))
    fields = records[0]._fields
    master_records = []

    if masterstream:
        # Link input records to master records
        master_records = list(excel.reader(masterstream))
        comparisons, indices, master_indices = link.between(
            comparator, indices, records, master_records)
        stat_indexing_between(indices, master_indices)
        write_indices(indices, odir, "1A-")
        write_indices(master_indices, odir, "1B-")
    else:
        # Link input records to themselves
        comparisons, indices = link.within(comparator, indices, records)
        stat_indexing_within(indices)
        write_indices(indices, odir, "1-")
        master_indices = indices

    matches, nonmatches = classifier(comparisons)
    
    if masterstream:
        matchrows, singlerows = split_records(matches, records)
        writecsv(opath('5-input-matchrows.csv'), fields, matchrows)
        writecsv(opath('5-input-singlerows.csv'), fields, singlerows)
    
    # Write the match and nonmatch pairs with scores
    with nested(open(opath("2-match-stat.csv"),'wb'),
                open(opath("2-match-orig.csv"),'wb')) as (scomp,sorig):
        write_comparisons(comparator, indices, master_indices, 
                          comparisons, matches, scomp, sorig)
    with nested(open(opath("3-nonmatch-stat.csv"),'wb'),
                open(opath("3-nonmatch-orig.csv"),'wb')) as (scomp,sorig):
        write_comparisons(comparator, indices, master_indices, 
                          comparisons, nonmatches, scomp, sorig)

    # Write groups of linked records
    with open(opath('4-groups.csv'),'wb') as ofile:
        recordgroups.write_csv(matches, records + master_records, fields, ofile)

