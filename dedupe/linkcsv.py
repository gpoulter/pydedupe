"""
:mod:`linkcsv` -- Record linkage using CSV outputs
==================================================

.. moduleauthor:: Graham Poulter
"""

import excel

def write_indices(indices, outdir, prefix):
    """Write indices in CSV format.

    :type indices: :class:`~indexer.Indices`
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
    
       >>> from .indexer import Indices,Index
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
    :type comparator: :class:`~sim.RecordSim`
    :param comparator: collection of named :class:`~sim.ValueSim` field comparators
    :type comparisons: {(`R`, `R`):[:class:`float`,...],...}
    :param comparisons: Similarity vectors from pairs of record comparisons.
    :type scores: {(`R`,`R`)::class:`float`,...} or :keyword:`None`
    :param scores: classifier scores to show for pairs of records.
    :type indices1: :class:`~indexer.Indices`
    :param indices1: index of records being linked
    :type indices2: :class:`~indexer.Indices`
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
    
    :type matchpairs: :class:`iter` [(`R`, `R`),...] 
    :param matchpairs: pairs of input and master records that matches
    :type records: [`R`,...]
    :param records: input records
    :rtype: [`R`,...], [`R`,...]
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
    
    
class LinkCSV:
    """Link the input records, either to themselves or to the master records
    if provided. 
    
    The analysis and results of the linkage are written to CSV files.
    
    The linkage strategy is parameterised by the `indeces`, `comparator`
    and `classifier`, and whether or not `master` records are present in
    addition to the input `records`.
    
    Log messages are written to the root logger, for which a FileHandler 
    also writes the messages to the output directory.
    
    :type indices: :class:`~indexer.Indices`
    :param indices: prototype for how to index records (copied with `.clone()`)
    :type comparator: :class:`~sim.RecordSim`, function(R,R) [float,...]
    :param comparator: calculates similarity vectors for record pairs.
    :type classifier: function({(`R`,`R`):[:class:`float`]}) [(`R`, `R`)], [(`R`, `R`)]
    :param classifier: separate record comparisons into matching and non-matching.
    :type records: [`R`,...]
    :param records: input records for linkage analysis
    :type odir: :class:`str`
    :param odir: Directory in which to place output files and log files.
    :type master: [`R`,...]
    :param master: master records to which `records` should be linked.
    """
    
    def __init__(self, odir, comparator, indices, classifier, records, master=None):
        """
        :rtype: {(R,R):float}, {(R,R):float}
        :return: classifier scores for match pairs and non-match pairs
        """
        self.comparator = comparator
        self.index_proto = indices
        self.classifier = classifier
        self.master = master if master else []
        self.records = records
        self.odir = odir
        filelog(self.opath('linkage.log'))
        import link
        if master:
            self.comparisons, self.indices, self.master_indices = link.between(
                self.comparator, self.index_proto, self.records, self.master)
        else:
            self.comparisons, self.indices = link.within(
                self.comparator, self.index_proto, self.records)
            self.master_indices = None 
        self.matches, self.nonmatches = classifier(self.comparisons)

    def opath(self, name):
        """Path for a file `name` in the :attr:`odir`."""
        import os
        return os.path.join(self.odir, name)
    
    @property
    def fields(self):
        """Fields on input records."""
        try:
            return self.records[0]._fields
        except (IndexError, AttributeError) as e:
            return None
    
    @property
    def master_fields(self):
        """Fields on master records."""
        try:
            return self.master[0]._fields
        except (IndexError, AttributeError) as e:
            return None
    
    def write_all(self):
        """Call `write_records`, `write_indices`, `write_input_splits`,
        `write_pairs` and `write_groups`, for all of the analysis. May
        take a long time and result in very large output directory."""
        self.write_records()
        self.write_indeces()
        self.write_input_splits()
        self.write_pairs()
        self.write_groups()
    
    def write_records(self):
        """Write records_input.csv and records_master.csv with the input records."""
        writecsv(self.opath("records_input.csv"), self.records, self.fields)
        if self.master:
            writecsv(self.opath("records_master.csv"), self.master, self.master_fields)
        
    def write_indeces(self):
        """Write InputIdx-* and MasterIdx-* for each index defined in indeces."""
        write_indices(self.indices, self.odir, "InputIdx-")
        if self.master:
            write_indices(self.master_indices, self.odir, "MasterIdx-")

    def write_input_splits(self):
        """Only valid for linking between input and master, it splits the
        input records across two files inputs-matched.csv and inputs-nomatch.csv
        for records that matched the master and records that dit not."""
        if self.master:
            matchrows, singlerows = split_records(self.matches, self.records)
            writecsv(self.opath('input-matchrows.csv'), matchrows, self.fields)
            writecsv(self.opath('input-singlerows.csv'), singlerows, self.fields)
            
    def write_pairs(self):
        """For all compared pairs, write the matching and non-matching
        comparisons to 'match-comparisons.csv' and 'nonmatch-comparisons.csv'
        Also write the pairs of matching and non-matching records
        to 'match-pairs.csv' and 'nonmatch-pairs.csv"""
        _ = self
        from contextlib import nested
        with nested(open(_.opath("match-comparisons.csv"),'wb'),
                    open(_.opath("match-pairs.csv"),'wb')) as (scomp,sorig):
            write_comparisons(scomp, _.comparator, _.comparisons, _.matches, 
                              _.indices, _.master_indices, _.fields, sorig)
        with nested(open(_.opath("nonmatch-comparisons.csv"),'wb'),
                    open(_.opath("nonmatch-pairs.csv"),'wb')) as (scomp,sorig):
            write_comparisons(scomp, _.comparator, _.comparisons, _.nonmatches, 
                              _.indices, _.master_indices, _.fields, sorig)
            
    def write_groups(self):
        """write the groups of linked records for manual review"""
        with open(self.opath('groups.csv'),'wb') as ofile:
            import recordgroups
            recordgroups.write_csv(
                self.matches, self.records+self.master, ofile, self.fields)

