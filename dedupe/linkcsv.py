"""
:mod:`linkcsv` -- Record linkage for CSV inputs
===============================================

.. module:: linkcsv
   :synopsis: Link records together from CSV file input.
.. moduleauthor:: Graham Poulter
"""

import logging, os
import excel, link, recordgroups 

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

def stat_indexing_within(indices, log=None):
    """Log expected within-index comparisons"""
    log = log if log else logging.getLogger()
    for name, index in indices.iteritems():
        log.info("Index %s may require up to %d comparisons.", name, 
                 index.count_comparisons())
        index_stats(index, name, log)

def stat_indexing_between(indices1, indices2, log=None):
    """Log expected between-index comparisons"""
    log = log if log else logging.getLogger()
    for (n1, i1), (n2, i2) in zip(self.items(), other.items()): 
        log.info("Index %s to %s may require up to %d comparisons.",
                 n1, n2, i1.count_comparisons(i2))
        index_stats(i1, "Input " + n1, log)
        index_stats(i2, "Master " + n2, log)

def write_comparisons(comparator, indices1, indices2, comparisons, scores, stream, origstream=None):
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
    :param scores: Classifier scores for pairs of records. Omitted in\
    the output if None.
    
    :type stream: binary Writer
    :param stream: Destination of comparison vectors in CSV format.
    
    :type origstream: binary Writer
    :param origstream: Destination of original records pairs in CSV format.
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
        writer.writerow([u""] + [u";".join(x) for x in keys1] + [ unicode(getvalue(rec1,f)) for f in field1 ])
        writer.writerow([u""] + [u";".join(x) for x in keys2] + [ unicode(getvalue(rec2,f)) for f in field2 ])
        # Tuple of booleans indicating whether index keys are equal
        idxmatch = [ bool(set(k1).intersection(set(k2))) if 
                     (k1 is not None and k2 is not None) else ""
                     for k1,k2 in zip(keys1,keys2) ]
        weightrow = [score] + idxmatch + list(weights)
        writer.writerow(str(x) for x in weightrow)
        if record_writer:
            record_writer.writerow(rec1)
            record_writer.writerow(rec2)   

def linkcsv(indices, comparator, classifier, inputfile, outputdir, masterfile=None):
    """Run a dedupe task using the specified indices, comparator and classifier.
    
    :type indices: :class:`Indices`
    :param indices: Index layout for the records.

    :type comparator: :class:`RecordSim`, function(R,R) [float,...]
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
        comparisons, indices, master_indices = link.between(
            comparator, indices, records, master_records)
        stat_indexing_between(indices1, indices2)
        write_indices(indices, outputdir, "1A-")
        write_indices(master_indices, outputdir, "1B-")
    else:
        # Dedupe input records against themselves
        comparisons, indices = link.within(comparator, indices, records)
        stat_indexing_within(indices)
        write_indices(indices, outputdir, "1-")
        master_indices = indices

    matches, nonmatches = classifier(comparisons)

    # Write the match and nonmatch pairs with scores
    write_comparisons(comparator,
        indices, master_indices, comparisons, matches, 
        outfile("2-matches.csv"), outfile("3-matches-orig.csv"))
    write_comparisons(comparator,
        indices, master_indices, comparisons, nonmatches, 
        outfile("2-nonmatches.csv"), outfile("3-nonmatches-orig.csv"))

    # Write groups of linked records
    recordgroups.write_csv(matches, records + master_records, 
                           records[0]._fields, outfile('4-groups.csv'))

