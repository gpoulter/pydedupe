"""Provide convenience functions for linking similar records.  

The "dedupe" function compares one set of records against itself, and the
"link" function compares it against a master set of records.

The "csvdedupe" convenience function identifies similar records in a 
CSV file, using a specified strategy for indexing records, comparing
records, and classifying the comparisons into matches and non-matches.

A "comparison" is a tuple of floats between 0.0  and 1.0, representing
the field-by-field similarity of a pair of records for the comparisons
defined in the L{indexer.RecordComparator}

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

import logging, os
import namedcsv
from recordgroups import writegroups

def makeoutputdir(dirname, open=open):
    """Create a directory and return opener factories for files
    in that directory."""
    if not os.path.exists(dirname): 
        os.mkdir(dirname)
    def outpath(filename):
        """Return path to named output file."""
        return os.path.join(dirname, filename)
    def outfile(filename):
        """Return write-only stream for named output file."""
        return open(outpath(filename), 'w')
    return outpath, outfile

def dedupe(records, indeces, comparator):
    """Dedupe records against itself.
    @param records: Iteration of record namedtuples.
    @param comparator: L{indexer.RecordComparator}
    @return: comparisons as (rec1,rec2):weights, and indeces as L{Indeces}
    """
    indeces.insert(records)
    logging.info("Dedupe index statistics follow...")
    indeces.log_index_stats()
    comparisons = comparator.dedupe(indeces)
    return comparisons, indeces


def link(records1, records2, indeces, comparator):
    """Link records1 against records2.
    @param records1, records2: Iterations of record namedtuples.
    @param indeces: L{indexer.Indeces}
    @param comparator: L{indexer.RecordComparator}
    @return: comparisons as (rec1,rec2):weights, and two Indeces instances
    """
    import copy
    def index(records):
        myindeces = copy.deepcopy(indeces)
        myindeces.insert(records)
        return myindeces
    indeces1, indeces2 = [ index(records) for records in (records1, records2) ]
    logging.info("Record linkage index statistics follow...")
    indeces1.log_index_stats(indeces2)
    comparisons = comparator.link(indeces1, indeces2)
    return comparisons, indeces1, indeces2


def csvdedupe(indeces, comparator, classifier, inputfile, outputdir, masterfile=None):
    """Run a dedupe task using the specified indeces, comparator and classifier.
    
    @param indeces: Instance of L{indexer.Indeces}.

    @param comparator: Instance of L{indexer.RecordComparator}, taking
    a pair of records and returning a similarity tuple.
    
    @param classifier: Function of a list of comparisons (as a mapping from
    similarity vector to pair of compared tuples) that returns two lists of
    records, one for matches and one for non-matches.
    
    @param inputfile: CSV file of input records to dedupe
    
    @param outputdir: Directory to log the output files to.
    
    @param masterfile: Optional CSV file of master records.  The output will
    instead list input records that are dups of the master records.
    """

    outpath, outfile = makeoutputdir(outputdir)
    
    ## Set up logging to file
    filehandler = logging.FileHandler(outpath("dedupe.log"))
    filehandler.setFormatter(
        logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(filehandler)

    ## Index records, compare pairs, identify match/nonmatch pairs
    records = list(namedcsv.ureader(inputfile))
    master_records = []

    if masterfile:
        ## Link input records to master records
        master_records = list(namedcsv.ureader(masterfile))
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
    writegroups(matches, records + master_records, fields, 
                outfile('4-groups.csv'))

