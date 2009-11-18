"""
:mod:`linkcsv` -- Record linkage for CSV inputs
===============================================

.. module:: linkcsv
   :synopsis: Link records together from CSV file input.
.. moduleauthor:: Graham Poulter
"""

import excel
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
    
       >>> from StringIO import StringIO
       >>> from contextlib import closing
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
    """Add filehandler to main logger, writing to :file:`{path}`."""
    import logging
    filehandler = logging.FileHandler(path)
    filehandler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(filehandler)

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

def linkcsv(comparator, indices, classifier, records, odir, master=None):
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
    :rtype: {(R,R):float}, {(R,R):float}
    :return: classifier scores for match pairs and non-match pairs
    """
    import os
    opath = lambda name: os.path.join(odir, name)
    fields = records[0]._fields if hasattr(records[0],"_fields") else None
    master = master if master else []
    filelog(opath('dedupe.log'))

    import link
    if master:
        # Link input records to master records
        comparisons, indices, master_indices = link.between(
            comparator, indices, records, master)
        #write_indices(indices, odir, "1A-")
        #write_indices(master_indices, odir, "1B-")
    else:
        # Link input records to themselves
        comparisons, indices = link.within(comparator, indices, records)
        #write_indices(indices, odir, "1-")
        master_indices = indices

    matches, nonmatches = classifier(comparisons)
    
    if master:
        matchrows, singlerows = split_records(matches, records)
        writecsv(opath('5-input-matchrows.csv'), matchrows, fields)
        writecsv(opath('5-input-singlerows.csv'), singlerows, fields)
    
    # Write the match and nonmatch pairs with scores
    from contextlib import nested
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
        import recordgroups 
        recordgroups.write_csv(matches, records+master, ofile, fields)
        
    return matches, nonmatches

