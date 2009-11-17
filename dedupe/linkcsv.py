"""
:mod:`linkcsv` -- Record linkage for CSV inputs
===============================================

.. module:: linkcsv
   :synopsis: Link records together from CSV file input.

.. moduleauthor:: Graham Poulter
"""

import logging, os
import excel
from recordgroups import write_csv

def makeoutputdir(dirname, open=open):
    """Create a directory and return opener factories for files
    in that directory.
    
    :type dirname: path string 
    :param dirname: Where to place the named files
    :rtype: function(name) abspath, function(name) file
    :return: output path generator and output file opener
    """
    if not os.path.exists(dirname): 
        os.mkdir(dirname)
    def outpath(filename):
        return os.path.join(dirname, filename)
    def outfile(filename):
        return open(outpath(filename), 'w')
    return outpath, outfile

def link_single(records, indices, comparator):
    """Find similar pairs within a set of records.
    
    :type records: [:class:`namedtuple`,...]
    :param records: records to be linked
    :type indices: :class:`Indices`
    :param indices: index layout for the records
    :type comparator: :class:`RecordComparator`
    :param comparator: how to compare records for similarity
    :rtype: {(R,R):[float,...]}, :class:`Indices`
    :return: Similarity vectors for pairwise comparisons, and the\
    indices used for comparison.
    """
    indices.insert(records)
    log_indexing_single(indices)
    comparisons = comparator.dedupe(indices)
    return comparisons, indices

def link_pair(records1, records2, indices, comparator):
    """Find similar pairs between two sets of records.
    
    :type records1: [:class:`namedtuple`,...]
    :param records1: left-hand records to link to right-hand
    :type records2: [:class:`namedtuple`,...]
    :param records2: right-hand being linked to
    :type indices: :class:`Indices`
    :param indices: prototypical index layout for the records
    :type comparator: :class:`RecordComparator`
    :param comparator: how to compare records for similarity
    :rtype: {(R,R):[float,...]}, :class:`Indices`, :class:`Indices`
    :return: Similarity vectors for pairwise comparisons, and the\
    corresponding indices for `records1` and `records2`.
    """
    import copy
    def new_index(records):
        r = copy.deepcopy(indices)
        r.insert(records)
        return r
    indices1, indices2 = new_index(records1), new_index(records2)
    log_indexing_pair(indices1, indices2)
    comparisons = comparator.link(indices1, indices2)
    return comparisons, indices1, indices2

def write_indices(indices, outdir, prefix):
    """Write indices in CSV format.
    :type indices: :class:`Indices`
    :param indices: Write one file per index in this dictionary.
    :param outdir: Write index files to this directory.
    :param prefix: Prepend string to each output file name
    """
    def write_index(index, stream):
        """Write a single index in CSV format to a stream"""
        writer = excel.writer(stream)
        for indexkey, rows in index.iteritems():
            for row in rows:
                writer.writerow((indexkey,) + row)
    from os.path import join
    for indexname, index in indices.iteritems():
        with open(join(outdir, prefix + indexname + '.csv'), 'wb') as stream:
            write_index(index, stream)

def index_stats(index, name, log=None):
    """Write statistics about the blocks of `index`, prefixing lines with
    `name`, to the `log` :class:`Logger`."""
    log = log if log else logging.getLogger()
    if not index:
        log.info("%s: index is empty." % name)
    else:
        records = sum(len(recs) for recs in index.itervalues())
        largest = max(len(recs) for recs in index.itervalues())
        blocks = len(index)
        log.info("%s: %d records, %d blocks. %d in largest block, %.2f per block.",
                 name, records, blocks, largest, float(records)/blocks)

def log_indexing_single(indices, log=None):
    """Log expected within-index comparisons"""
    log = log if log else logging.getLogger()
    for name, index in indices.iteritems():
        log.info("Index %s needs up to %d comparisons.", name, 
                 index.count_comparisons())
        index_stats(index, name, log)

def log_indexing_pair(indices1, indices2, log=None):
    """Log expected between-index comparisons"""
    log = log if log else logging.getLogger()
    for (n1, i1), (n2, i2) in zip(self.items(), other.items()): 
        log.info("Index %s to %s needs %d comparisons.",
                 n1, n2, i1.count_comparisons(i2))
        index_stats(i1, "Input " + n1, log)
        index_stats(i2, "Master " + n2, log)

def csvdedupe(indices, comparator, classifier, inputfile, outputdir, masterfile=None):
    """Run a dedupe task using the specified indices, comparator and classifier.
    
    :type indices: :class:`Indices`
    :param indices: Index layout for the records.

    :type comparator: :class:`RecordComparator`, function(R,R) [float,...]
    :param comparator: Obtain similarity vectors for record pairs.
    
    :type classifier: function({(R,R):[float,...],...}) -> [(R,R),...], [(R,R),...]
    :param classifier: Takes pairs of record comparisons and separates\
    it into pairs that match and pairs that don't match.
    
    :type inputfile: path string
    :param inputfile: CSV input records for left-hand records.
    
    :type outputdir: path string
    :param outputdir: Destination directory for output files.

    :type masterfile: path string
    :param masterfile: Optional CSV of master records, to be used as right-hand\
    records against which the `inputfile` records will be linked.
    """
    outpath, outfile = makeoutputdir(outputdir)
    
    # Set up logging to file
    filehandler = logging.FileHandler(outpath("dedupe.log"))
    filehandler.setFormatter(
        logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(filehandler)

    # Index records, compare pairs, identify match/nonmatch pairs
    records = list(excel.reader(inputfile))
    master_records = []

    if masterfile:
        # Link input records to master records
        master_records = list(excel.reader(masterfile))
        comparisons, indices, master_indices = link_pair(
            records, master_records, indices, comparator)
        write_indices(indices, outputdir, "1A-")
        write_indices(master_indices, outputdir, "1B-")
    else:
        # Dedupe input records against themselves
        comparisons, indices = link_single(records, indices, comparator)
        write_indices(indices, outputdir, "1-")
        master_indices = indices

    matches, nonmatches = classifier(comparisons)

    # Write the match and nonmatch pairs with scores
    comparator.write_comparisons(
        indices, master_indices, comparisons, matches, 
        outfile("2-matches.csv"), outfile("3-matches-orig.csv"))
    comparator.write_comparisons(
        indices, master_indices, comparisons, nonmatches, 
        outfile("2-nonmatches.csv"), outfile("3-nonmatches-orig.csv"))

    # Classify and output
    fields = records[0]._fields
    write_csv(matches, records + master_records, fields, 
                outfile('4-groups.csv'))

