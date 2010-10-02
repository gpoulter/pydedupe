"""
Helpers for record linkage with CSV files for input and output
==============================================================

.. moduleauthor:: Graham Poulter
"""

import logging, os
import csv, group, sim


def write_indices(indices, outdir, prefix):
    """Write indices in CSV format.

    :type indices: :class:`~indexer.Indices`
    :param indices: write one file per index in this dictionary.
    :type outdir: :class:`str`
    :param outdir: write index files to this directory.
    :type prefix: :class:`str`
    :param prefix: prepend this to each output file name.

    >>> from dedupe import linkcsv, csv, block, sim
    >>> makekey = lambda r: [int(r[1])]
    >>> compare = lambda x, y: float(int(x[1])==int(y[1]))
    >>> records = [('A', 5.5), ('C', 5.25)]
    >>> indexstrategy = [ ("Idx", block.Index, makekey) ]
    >>> indices = sim.Indices(indexstrategy, records)
    >>> streams = csv._fake_open(linkcsv)
    >>> linkcsv.write_indices(indices, outdir="/tmp", prefix="foo-")
    >>> stream = streams["/tmp/foo-Idx.csv"]
    >>> stream.seek(0)
    >>> list(csv.Reader(stream, fields='Idx V1 V2'))
    [Row(Idx=u'5', V1=u'A', V2=u'5.5'), Row(Idx=u'5', V1=u'C', V2=u'5.25')]
    """
    def write_index(index, stream):
        """Write a single index in CSV format to a stream"""
        writer = csv.Writer(stream)
        for indexkey, rows in index.iteritems():
            for row in rows:
                writer.writerow([unicode(indexkey)] + [unicode(v) for v in row])
    from os.path import join
    for indexname, index in indices.iteritems():
        with open(join(outdir, prefix+indexname+'.csv'), 'wb') as stream:
            write_index(index, stream)


def write_comparisons(ostream, comparator, comparisons, scores, indices1,
                      indices2=None, projection=None, origstream=None):
    """Write pairs of compared records, together with index keys and
    field comparison weights.  Inspection shows which index keys matched,
    and the field-by-field similarity.

    :type ostream: binary writer
    :param ostream: where to write CSV for similarity vectors.
    :type comparator: :class:`~sim.Record`
    :param comparator: dict of named :class:`~sim.Field` field comparators
    :type comparisons: {(`R`, `R`):[:class:`float`, ...], ...}
    :param comparisons: Similarity vectors from pairs of record comparisons.
    :type scores: {(`R`, `R`)::class:`float`, ...} or :keyword:`None`
    :param scores: classifier scores to show for pairs of records.
    :type indices1: :class:`~indexer.Indices`
    :param indices1: index of records being linked
    :type indices2: :class:`~indexer.Indices`
    :param indices2: optional index of right-hand records for master-linkage.
    :type projection: :class:`Projection`
    :param projection: Converts each record into output form.
    :type origstream: binary writer
    :param origstream: where to write CSV for pairs of compared original records.
    """
    if not comparisons: return # in case no comparisons were done
    # File for comparison statistics
    writer = csv.Writer(ostream)
    writer.writerow(["Score"] + indices1.keys() + comparator.keys())
    indices2 = indices2 if indices2 else indices1
    # File for original records
    record_writer = None
    # Obtain field-getter for each value comparator
    field1 = [ vcomp.field1 for vcomp in comparator.itervalues() ]
    field2 = [ vcomp.field2 for vcomp in comparator.itervalues() ]
    # Use dummy classifier scores if None were provided
    if scores is None:
        scores = dict((k, 0) for k in comparisons.iterkeys())
    # wrtie the similarity vectors
    for (rec1, rec2), score in scores.iteritems():
        weights = comparisons[(rec1, rec2)] # look up comparison vector
        keys1 = [ idx.makekey(rec1) for idx in indices1.itervalues() ]
        keys2 = [ idx.makekey(rec2) for idx in indices2.itervalues() ]
        writer.writerow([u""] +
            [u";".join(unicode(k) for k in kl) for kl in keys1] +
            [ unicode(f(rec1)) for f in field1 ])
        writer.writerow([u""] +
            [u";".join(unicode(k) for k in kl) for kl in keys2] +
            [ unicode(f(rec2)) for f in field2 ])
        # Tuple of booleans indicating whether index keys are equal
        idxmatch = [ bool(set(k1).intersection(set(k2))) if
                     (k1 is not None and k2 is not None) else ""
                     for k1, k2 in zip(keys1, keys2) ]
        weightrow = [score] + idxmatch + list(weights)
        writer.writerow(str(x) for x in weightrow)
    if origstream is not None:
        record_writer = csv.Writer(origstream)
        if projection:
            record_writer.writerow(projection.fields)
        else:
            projection = lambda x: x # no transformation
        for (rec1, rec2), score in scores.iteritems():
            record_writer.writerow(projection(rec1))
            record_writer.writerow(projection(rec2))


def filelog(path):
    """Add filehandler to main logger, writing to :file:`{path}`."""
    import logging
    filehandler = logging.FileHandler(path)
    filehandler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(filehandler)


def writecsv(path, rows, header=None):
    """Write the `header` and `rows` to csv file at `path`"""
    from . import csv
    with open(path, 'wb') as out:
        writer = csv.Writer(out)
        if header: writer.writerow(header)
        writer.writerows(rows)


def loadcsv(path):
    """Load records from csv at `path` as a list of :class:`namedtuple`"""
    from . import csv
    with open(path, 'rb') as istream:
        return list(csv.Reader(istream))


class LinkCSV(object):
    """Link the input records, either to themselves or to the master records
    if provided.

    The linkage is performed in the constructor, which may therefore take a
    long time to return. The `write_*` methods tell the instance which results
    to write to CSV files. The strategy for linkage is made up of the
    `indeces`, `comparator` and `classifier` parameters.  Progress
    messages and estimates are written to the root logger, for which
    a FileHandler directs output to the output directory.

    :type indexstrategy: [ (`str`, `type`, `function`) ]
    :param indexstrategy: List of indexes to use, providing the index name, \
    the class for constructing the index, and the function for producing the index key.
    :type comparator: :class:`~sim.Record`
    :param comparator: takes a pair of records and returns a similarity vector.
    :type classifier: function({(`R`, `R`):[:class:`float`]}) [(`R`, `R`)], [(`R`, `R`)]
    :param classifier: separate record comparisons into matching and non-matching.
    :type records: [`R`, ...]
    :param records: input records for linkage analysis
    :type odir: :class:`str` or :keyword:`None`
    :param odir: Directory in which to place output files and log files.
    :type master: [`R`, ...]
    :param master: master records to which `records` should be linked.
    :type logname: :class:`str` or :keyword:`None`
    :param logname: Name of log file to write to in output directory.

    :type indeces1, indeces2: :class:`~sim.Indeces`
    :ivar indeces1, indeces2: Indexed input and master records.
    :type matches, nonmatches: {(`R`, `R`)::class:`float`}
    :ivar matches, nonmatches: classifier scores of matched/nonmatched pairs.
    """

    def __init__(self, outdir, indexstrategy, comparator, classifier, records,
                 master=None, logname='linkage.log'):
        """
        :rtype: {(R, R):float}, {(R, ):float}
        :return: classifier scores for match pairs and non-match pairs
        """
        self.comparator = comparator
        self.indexstrategy = indexstrategy
        self.classifier = classifier
        self.records1 = records
        self.records2 = master if master else []
        self.outdir = outdir
        if self.outdir is not None and logname is not None:
            filelog(self.opath(logname))
        # Index the records and print the stats
        self.indices1 = sim.Indices(self.indexstrategy, self.records1)
        self.indices2 = None
        if self.records2:
            self.indices2 = sim.Indices(self.indexstrategy, self.records2)
        # Compute the similarity vectors
        self.indices1.log_comparisons(self.indices2)
        self.comparisons = self.indices1.compare(self.comparator, self.indices2)
        # Classify the similarity vectors
        self.matches, self.nonmatches = classifier(self.comparisons)

    def opath(self, name):
        """Path for a file `name` in the :attr:`odir`."""
        import os
        return os.path.join(self.outdir, name)

    @property
    def fields1(self):
        """Field names on input records."""
        try:
            return self.records1[0]._fields
        except (IndexError, AttributeError) as e:
            return []

    @property
    def fields2(self):
        """Field names on master records."""
        try:
            return self.records2[0]._fields
        except (IndexError, AttributeError) as e:
            return []

    @property
    def projection(self):
        """Projection instance to convert input/master records into output records."""
        if self.fields1:
            from . import csv
            return csv.Projection.unionfields(self.fields2, self.fields1)
        else:
            return None

    def write_all(self):
        """Call all of the other `write_*` methods, for full analysis.

        .. warning::
           The total output may be as much as 10x larger than the input file.
        """
        self.write_records()
        self.write_indeces()
        if self.records2:
            self.write_input_splits()
        self.write_match_pairs()
        self.write_nonmatch_pairs()
        self.write_groups()

    def write_records(self, inputrecs="input-records.csv", masterrecs="input-master.csv"):
        """Write the input and master records CSV files."""
        writecsv(self.opath(inputrecs), self.records1, self.fields1)
        if self.indices2:
            writecsv(self.opath(masterrecs), self.records2, self.fields2)

    def write_indeces(self, inputpre="InputIdx-", masterpre="MasterIdx-"):
        """Write contents of each :class:`~indexer.Index` to files starting with these prefixes."""
        write_indices(self.indices1, self.outdir, inputpre)
        if self.indices2:
            write_indices(self.indices2, self.outdir, masterpre)

    def write_input_splits(self, matches='input-matchrows.csv', singles='input-singlerows.csv'):
        """Write input records that matched and did not match master (requires
        that `master` was specified)."""
        matchset = set(a for a, b in self.matches)
        matchrows = [r for r in self.records1 if r in matchset]
        singlerows = [r for r in self.records1 if r not in matchset]
        writecsv(self.opath(matches), matchrows, self.fields1)
        writecsv(self.opath(singles), singlerows, self.fields1)

    def write_match_pairs(self, comps="match-comparisons.csv", pairs="match-pairs.csv"):
        """For matched pairs, write the record comparisons and original record pairs."""
        _ = self
        from contextlib import nested
        with nested(open(_.opath(comps), 'wb'),
                    open(_.opath(pairs), 'wb')) as (o_comps, o_pairs):
            write_comparisons(o_comps, _.comparator, _.comparisons, _.matches,
                              _.indices1, _.indices2, self.projection, o_pairs)

    def write_nonmatch_pairs(self, comps="nonmatch-comparisons.csv", pairs="nonmatch-pairs.csv"):
        """For non-matched pairs, write the record comparisons and original record pairs."""
        _ = self
        from contextlib import nested
        with nested(open(_.opath(comps), 'wb'),
                    open(_.opath(pairs), 'wb')) as (o_comps, o_pairs):
            write_comparisons(o_comps, _.comparator, _.comparisons, _.nonmatches,
                              _.indices1, _.indices2, self.projection, o_pairs)

    def write_groups(self, groups="groups.csv"):
        """Write out all records, with numbered groups of mutually linked records first."""
        with open(self.opath(groups), 'wb') as ofile:
            import group
            group.write_csv(
                self.matches, self.records1+self.records2, ofile, self.projection)
