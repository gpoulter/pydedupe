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

from namedcsv import makeoutputdir, NamedCSVReader
from recordgroups import writegroups
import logging

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


def csvdedupe(indeces, comparator, classifier, inputfile, outputdir):
    """Run a dedupe task using the specified indeces, comparator and classifier.
    
    @param indeces: Instance of L{indexer.Indeces}.

    @param comparator: Instance of L{indexer.RecordComparator}, taking
    a pair of records and returning a similarity tuple.
    
    @param classifier: Function of a list of comparisons (as a mapping from
    similarity vector to pair of compared tuples) that returns two lists of
    records, one for matches and one for non-matches.
    
    @param inputfile: CSV file of input records to dedupe
    
    @param outputdir: Directory to log the output files to.
    """

    outpath, outfile = makeoutputdir(outputdir)
    
    ## Set up logging to file
    filehandler = logging.FileHandler(outpath("dedupe.log"))
    filehandler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(filehandler)

    ## Index records, compare pairs, identify match/nonmatch pairs
    records = list(NamedCSVReader(inputfile))
    comparisons, myindeces = dedupe(records, indeces, comparator)
    myindeces.write_csv(outpath("1-"))
    matches, nonmatches = classifier(comparisons)

    ## Write the match and nonmatch pairs with scores
    comparator.write_comparisons(
        myindeces, myindeces, comparisons, matches, 
        outfile("2-matches.csv"), outfile("3-matches-orig.csv"))
    comparator.write_comparisons(
        myindeces, myindeces, comparisons, nonmatches, 
        outfile("2-nonmatches.csv"), outfile("3-nonmatches-orig.csv"))

    ## Classify and output
    fields = records[0]._fields
    writegroups(matches, records, fields, outfile('4-groups.csv'))
