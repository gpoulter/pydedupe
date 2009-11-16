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

def dedupe(records, indeces, comparator):
    """Find similar pairs within a set of records.
    
    :type records: [:class:`namedtuple`,...]
    :param records: records to be linked
    :type indeces: :class:`Indeces`
    :param indeces: index layout for the records
    :type comparator: :class:`RecordComparator`
    :param comparator: how to compare records for similarity
    :rtype: {(R,R):[float,...]}, :class:`Indeces`
    :return: Similarity vectors for pairwise comparisons, and the\
    indeces used for comparison.
    """
    indeces.insert(records)
    logging.info("Dedupe index statistics follow...")
    indeces.log_index_stats()
    comparisons = comparator.dedupe(indeces)
    return comparisons, indeces

def link(records1, records2, indeces, comparator):
    """Find similar pairs between two sets of records.
    
    :type records1: [:class:`namedtuple`,...]
    :param records1: left-hand records to link to right-hand
    :type records2: [:class:`namedtuple`,...]
    :param records2: right-hand being linked to
    :type indeces: :class:`Indeces`
    :param indeces: prototypical index layout for the records
    :type comparator: :class:`RecordComparator`
    :param comparator: how to compare records for similarity
    :rtype: {(R,R):[float,...]}, :class:`Indeces`, :class:`Indeces`
    :return: Similarity vectors for pairwise comparisons, and the\
    corresponding indeces for `records1` and `records2`.
    """
    import copy
    def index(records):
        myindeces = copy.deepcopy(indeces)
        myindeces.insert(records)
        return myindeces
    indeces1, indeces2 = index(records1), index(records2)
    logging.info("Record linkage index statistics follow...")
    indeces1.log_index_stats(indeces2)
    comparisons = comparator.link(indeces1, indeces2)
    return comparisons, indeces1, indeces2

def csvdedupe(indeces, comparator, classifier, inputfile, outputdir, masterfile=None):
    """Run a dedupe task using the specified indeces, comparator and classifier.
    
    :type indeces: :class:`Indeces`
    :param indeces: Index layout for the records.

    :type comparator: :class:`RecordComparator`, function(R,R) [float,...]
    :param comparator: Obtain similarity vectors for record pairs.
    
    :type classifier: function({(R,R):[float,...],...}) -> [(R,R),...], [(R,R),...]
    :param classifier: Takes pairs of record comparisons and separates\
    it into pairs that match and pairs that don't match.
    
    :type intuptfile: path string
    :param inputfile: CSV input records for left-hand records.
    
    :type outputdir: path string
    :param outputdir: Destination directory for output files.

    :type masterfile: path string
    :param masterfile: Optional CSV of master records, to be used as right-hand\
    records against which the `inputfile` records will be linked.
    """

    outpath, outfile = makeoutputdir(outputdir)
    
    ## Set up logging to file
    filehandler = logging.FileHandler(outpath("dedupe.log"))
    filehandler.setFormatter(
        logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(filehandler)

    ## Index records, compare pairs, identify match/nonmatch pairs
    records = list(excel.reader(inputfile))
    master_records = []

    if masterfile:
        ## Link input records to master records
        master_records = list(excel.reader(masterfile))
        comparisons, indeces, master_indeces = link(
            records, master_records, indeces, comparator)
        master_indeces.write_csv(outpath("1B-"))
    else:
        ## Dedupe input records against themselves
        comparisons, indeces = dedupe(records, indeces, comparator)
        master_indeces = indeces

    indeces.write_csv(outpath("1A-"))
    matches, nonmatches = classifier(comparisons)

    ## Write the match and nonmatch pairs with scores
    comparator.write_comparisons(
        indeces, master_indeces, comparisons, matches, 
        outfile("2-matches.csv"), outfile("3-matches-orig.csv"))
    comparator.write_comparisons(
        indeces, master_indeces, comparisons, nonmatches, 
        outfile("2-nonmatches.csv"), outfile("3-nonmatches-orig.csv"))

    ## Classify and output
    fields = records[0]._fields
    write_csv(matches, records + master_records, fields, 
                outfile('4-groups.csv'))

