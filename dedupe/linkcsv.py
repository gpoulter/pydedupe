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
    
    .. testsetup::
    
       >>> io = StringIO() # the 'file'
       >>> io.close = lambda: None # disable closing
       >>> import linkcsv # patch module
       >>> linkcsv.open = lambda f,m: closing(io)
       >>> def magic(fields):
       ...    io.seek(0)
       ...    return list(excel.reader(io, fields=fields))
       
    .. doctest::
    
       >>> makekey = lambda r: [int(r[1])]
       >>> compare = lambda x,y: float(int(x[1])==int(y[1]))
       >>> indices = Indices(("Idx",Index(makekey, [('A',5.5),('C',5.25)])))
       >>> write_indices(indices, outdir="/tmp", prefix="foo")
       >>> magic('Idx V1 V2') # magically read fake '/tmp/foo-Idx.csv'
       [Row(Idx=u'5', V1=u'A', V2=u'5.5'), Row(Idx=u'5', V1=u'C', V2=u'5.25')]
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

def write_comparisons(ostream, comparator, comparisons, scores, indices1, 
                      indices2=None, fields=None, origstream=None):
    """Write pairs of compared records, together with index keys and 
    field comparison weights.  Inspection shows which index keys matched,
    and the field-by-field similarity.
    
    :type ostream: binary writer
    :param ostream: where to write CSV for similarity vectors.
    :type comparator: :class:`comp.Record`
    :param comparator: collection of named :class:`comp.ValueSim` field comparators
    :type comparisons: {(R,R):[float,...],...}
    :param comparisons: Similarity vectors from pairs of record comparisons.
    :type scores: {(R,R):float,...} or :keyword:`None`
    :param scores: classifier scores to show for pairs of records.
    :type indices1: :class:`Indices`, {str:{obj:[R,...],...},...}
    :param indices1: index of records being linked
    :type indices2: :class:`Indices`, {str:{obj:[R,...],...},...}
    :param indices2: optional index of right-hand records for master-linkage.
    :type fields: [:class:`str`,...]
    :param fields: header fields for writing original records to CSV
    :type origstream: binary writer
    :param origstream: where to write CSV for pairs of compared original records.
    """
    if not comparisons: return # in case no comparisons were done
    from sim import getvalue # for getting record fields
    # File for comparison statistics
    writer = excel.writer(ostream)
    writer.writerow(["Score"] + indices1.keys() + comparator.keys())
    indices2 = indices2 if indices2 else indices1
    # File for original records
    record_writer = None
    if origstream is not None:
        record_writer = excel.writer(origstream)
        if fields: record_writer.writerow(fields)
    # Obtain field-getter for each value comparator
    field1 = [ vcomp.field1 for vcomp in comparator.itervalues() ]
    field2 = [ vcomp.field2 for vcomp in comparator.itervalues() ]
    # Use dummy classifier scores if None were provided
    if scores is None:
        scores = dict((k,0) for k in comparisons.iterkeys())
    # wrtie the similarity vectors
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
    
def writecsv(path, rows, header=None):
    """Write the `header` and `rows` to csv file at `path`"""
    with open(path, 'wb') as out:
        writer = excel.writer(out)
        if header: writer.writerow(header)
        writer.writerows(rows)
        
def loadcsv(path):
    """Load records from csv at `path` as a list of :class:`namedtuple`"""
    with open(path, 'rb') as istream:
        return list(excel.reader(istream))

def linkcsv(comparator, indices, classifier, records, odir, master=None, logger=None):
    """Run a dedupe task using the specified indices, comparator and classifier.
    
    :type indices: :class:`Indices`
    :param indices: prototype for how to index records (copied with `.clone()`)
    :type comparator: :class:`RecordSim`, function(R,R) [float,...]
    :param comparator: calculates similarity vectors for record pairs.
    :type classifier: function({(R,R):[float]}) [(R,R)], [(R,R)]
    :param classifier: separate record comparisons into matching and non-matching.
    :type records: [R,...]
    :param records: input records for linkage analysis
    :type odir: :class:`string`
    :param odir: Directory in which to open output files.
    :type master: [R,...]
    :param master: master records to which `records` should be linked.
    :type logger: :class:`Logger` or :keyword:`None`
    :param logger: Log to write to, else set up :file:`{odir}/dedupe.log`
    :rtype: {(R,R):float}, {(R,R):float}
    :return: classifier scores for match pairs and non-match pairs
    """
    opath = lambda name: os.path.join(odir, name)
    logger = logger if logger else filelog(opath('dedupe.log'))
    fields = records[0]._fields if hasattr(records[0],"_fields") else None
    master = master if master else []

    if master:
        # Link input records to master records
        comparisons, indices, master_indices = link.between(
            comparator, indices, records, master)
        stat_indexing_between(indices, master_indices)
        #write_indices(indices, odir, "1A-")
        #write_indices(master_indices, odir, "1B-")
    else:
        # Link input records to themselves
        comparisons, indices = link.within(comparator, indices, records)
        stat_indexing_within(indices)
        #write_indices(indices, odir, "1-")
        master_indices = indices

    matches, nonmatches = classifier(comparisons)
    
    if master:
        matchrows, singlerows = split_records(matches, records)
        writecsv(opath('5-input-matchrows.csv'), matchrows, fields)
        writecsv(opath('5-input-singlerows.csv'), singlerows, fields)
    
    # Write the match and nonmatch pairs with scores
    with nested(open(opath("2-match-stat.csv"),'wb'),
                open(opath("2-match-orig.csv"),'wb')) as (scomp,sorig):
        write_comparisons(scomp, comparator, comparisons, matches, 
                          indices, master_indices, fields, sorig)
    with nested(open(opath("3-nonmatch-stat.csv"),'wb'),
                open(opath("3-nonmatch-orig.csv"),'wb')) as (scomp,sorig):
        write_comparisons(scomp, comparator, comparisons, nonmatches, 
                          indices, master_indices, fields, sorig)

    # Write groups of linked records
    with open(opath('4-groups.csv'),'wb') as ofile:
        recordgroups.write_csv(matches, records+master, ofile, fields)
        
    return matches, nonmatches

