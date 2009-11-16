"""
:mod:`indexer` -- Inverted index of records
===========================================

Inverted index of records, and comparator of records that can use
an inverted index to reduce the required number of comparisons.

Record ID is always assumed to be the first field of a record.

.. moduleauthor:: Graham Poulter


"""

from __future__ import with_statement

import logging
from compat import namedtuple, OrderedDict
import excel

class Index(dict):
    """A dictionary mapping index keys to a list of records that were
    inserted with that index key.
    
    The makekey function takes a record and returns a list of keys
    under which the record should be indexed.  For something like soundex
    there would only be one key in the list, but double-metaphone might
    return two keys, and n-gram combinations always return several keys."""
    
    def __init__(self, makekey):
        """Initialise the Index. 
        
        :param makekey: Function :func:`makekey`
        
        .. function:: makekey(record)
           :arg record: Record tuple
           :return: List of keys under which to index the record.
        """
        super(Index, self).__init__()
        self.makekey = makekey
        
    def insert(self, record):
        """Index a record by its keys. Only indexes keys for which bool(key)
        evaluates to True, meaning that keys such as False, 0, "", None are
        not included in the index.
        
        :param record: The record object to index.
        :return: The sequence of keys under which the record was inserted.
        """
        keys = self.makekey(record)
        assert isinstance(keys, tuple) or isinstance(keys, list) or isinstance(keys, set)
        for key in keys:
            if key is None or key == "":
                raise ValueError("Empty index key in %s" % repr(keys))
            recordsforkey = self.setdefault(key, list())
            recordsforkey.append(record)
        return keys
    
    def count_comparisons(self, other=None):
        """Count the number of comparisons implied by the index.  By default
        count the maximum pairwise comparisons for dedupe of this index 
        against itself.
        
        Due to caching, fewe comparisons may in fact take place when records
        appear in multiple index blocks.

        :param other: Optional :class:`Index` to compare against.
        
        :return: Maximum pairwise comparisons that need to be made.
        """
        comparisons = 0
        if not other or (other is self):
            # Count up comparisons to be made within this set of records.
            for recs in self.itervalues():
                if len(recs) > 1:
                    comparisons += len(recs)*(len(recs)-1)//2
        else:
            # Count up comparisons to be made to another set of records.
            for key in self:
                if key in other:
                    comparisons += len(self[key]) * len(other[key])
        return comparisons
    
    def log_block_statistics(self, prefix="", log=None):
        """Log statistics about the average and largest block sizes
        
        :param prefix: Print before the log message.
        :param log: Logging object to use.
        """
        if log is None: log = logging.getLogger()
        if not self:
            log.info("The index is empty.")
        else:
            nrecords = sum(len(recs) for recs in self.itervalues())
            biggroup = max(len(recs) for recs in self.itervalues())
            nkeys = len(self)
            log.info(prefix + "%d records in %d blocks. Largest block: %d, Average block: %.2f",
                     nrecords, nkeys, biggroup, float(nrecords)/nkeys)
        
    def dedupe(self, compare, comparisons=None):
        """Perform dedupe comparisons on the index.  Note that this sorts
        the lists of records in each index key to ensure that rec1<rec2 
        in each resulting comparison tuple.
        
        :param compare: Comparison function
        :type compare: Function of record pair, returning vector of similarities.
        
        :param comparisons: Cache of comparisons, mapping (rec1,rec2)\
        to similarity vector, where rec1 < rec2.
        """
        if comparisons is None:
            comparisons = {}
        for indexkey, records in self.iteritems():
            records.sort()
            for j in range(len(records)):
                for i in range(j):
                    # i < j, and sorting means record[i] <= record[j]
                    a,b = records[i], records[j] 
                    # same record indexed under multiple keys!
                    if a is b: continue
                    # now compare a and b, keeping a <= b
                    if (a,b) not in comparisons:
                        comparisons[(a,b)] = compare(a,b)
        return comparisons
                        
    def link(self, other, compare, comparisons=None):
        """Perform linkage comparisons for this index against the other index.
        
        :param other: Index object against which to perform linkage comparison.
        
        :param compare: Function of two records returning a similarity vector\
        such as [0.3,0.8,1.0,...].
        
        :param comparisons: Cache of comparisons mapping (rec1,rec2) to\
        similarity vector. Inserted pairs will have rec1 from self and rec2\
        from other.
        """
        if comparisons is None:
            comparisons = {}
        for indexkey in self.iterkeys():
            if indexkey in other.iterkeys():
                for rec1 in self[indexkey]:
                    for rec2 in other[indexkey]:
                        pair = (rec1, rec2)
                        if pair not in comparisons:
                            comparisons[pair] = compare(*pair)
        return comparisons
                            
    def write_csv(self, stream):
        """Write the contents of this index in CSV format to the given stream."""
        writer = excel.writer(stream)
        for indexkey, rows in self.iteritems():
            for row in rows:
                writer.writerow((indexkey,) + row)


class Indeces(OrderedDict):
    """Represents multiple Index instances as an ordered dictionary."""

    def __init__(self, *indeces):
        """Takes a number of (indexname, index) pairs as arguments."""
        OrderedDict.__init__(self)
        for key, value in indeces:
            self[key] = value
    
    def insert(self, records):
        """Insert the iteration of records in each Index."""
        for record in records:
            for index in self.itervalues():
                index.insert(record)
                
    def log_index_stats(self, other=None, log=None):
        """Log statistics and expected number of comparisons about the indeces.
        
        :param other: Index being compared against, set :keyword:`None` for self-compare.
        :type other: Instance of :class:`Indeces` (ordered dict of Index)
        """
        if log is None: log = logging.getLogger()
        # Loop over pairs of corresponding indeces
        for (i1name, index1), (i2name, index2) in \
            zip(self.items(), other.items() if other else self.items()): 
            num_comparisons = index1.count_comparisons(index2)
            log.info("Comparing %s to %s needs %d comparisons.", i1name, i2name, num_comparisons)
            index1.log_block_statistics(" Input %s: " % i1name, log)
            if other:
                index2.log_block_statistics(" Master %s: " % i2name, log)
            
    def write_csv(self, basepath):
        """Write the contents of the index dictionaries in CSV format."""
        for indexname, index in self.iteritems():
            with open(basepath + indexname + ".csv", "w") as stream:
                index.write_csv(stream)



class RecordComparator(OrderedDict):
    """Ordered dictionary mapping comparison weight fields to field comparison
    functions. The compare methods then compare pairs of records using those
    functions, returning namedtuple vectors corresponding to the
    results of each comparison function applied to the record.
    
    :ivar: Weights: Namedtuple type of the similarity vector, with field names\
    provided in the constructor.
    """
    
    def __init__(self, *comparators):
        """Parameteries with a variable number of (weight field, comparison
        function) pairs that will be applied to each pair of records."""
        super(RecordComparator, self).__init__(comparators)
        self.Weights = namedtuple("Weights", self.keys())

    def compare(self, recordA, recordB):
        """Compare two records and return a tuple of type Weights."""
        return self.Weights._make(
            comparator(recordA, recordB) for comparator in self.itervalues())
    
    __call__ = compare
    
    def allpairs(self, records):
        """Compare all distinct pairs of records given a single in a list of records.

        :param records: List of record namedtuples.

        :return: Mapping pairs (record1, record2) to L{Weights} similarity vector.
        """
        comparisons = {}
        for i in range(len(records)):
            for j in range(i):
                rec1, rec2 = records[i], records[j]
                assert rec1[0] != rec2[0]
                pair = tuple(sorted([rec1,rec2], key=lambda x:x[0]))
                if pair not in comparisons:
                    comparisons[pair] = self.compare(rec1, rec2)
        return comparisons

    def dedupe(self, indeces):
        """Compare records against themselves, using indexing to reduce number
        of comparisons and caching to avoid comparing same two records twice.
        
        :return: Map from compared (record1,record2) to L{Weights} vector.\
        Each compared tuple is lexicographically ordered (record1 < record2).
        """
        comparisons = {} # Map from (record1,record2) to L{Weights}
        for index in indeces.itervalues():
            index.dedupe(self.compare, comparisons)
        return comparisons
    

    def link(self, indeces1, indeces2):
        """Compare two sets of records using indexing to reduce number of comparisons.
        
        :param indeces1: List of L{Index} objects for first dataset.
        
        :param indeces2: List of L{Index} objects for second data set.

        :return: Map from (rec1,rec2) to comparison weights. The tuple has\
        rec1 from indeces1 and rec2 from indeces2, unlike\
        compare_indexed_single where (rec1,rec2) is ordered lexicographically.
        """
        assert indeces1 is not indeces2 # Must be different!
        comparisons = {}
        for index1, index2 in zip(indeces1.itervalues(), indeces2.itervalues()):
            index1.link(index2, self.compare, comparisons)
        return comparisons


    def write_comparisons(self, indeces1, indeces2, comparisons, scores, stream, origstream=None):
        """Write pairs of compared records, together with index keys and 
        field comparison weights.  Inspection shows which index keys matched,
        and the field-by-field similarity.
        
        :param indeces1: L{Indeces} for the left-hand records
        
        :param indeces2: L{Indeces} for the right-hand records for linkage.\
        Use the same as indeces1 in the case of dedupe.

        :param comparisons: Map from (rec1,rec2) to similarity vector.

        :param scores: Map from (rec1,rec2) to classifier score.  Only output\
        the pairs found in scores.  If None, output all without classifier score.
        
        :param stream: Output stream for the detailed comparison results.
        
        :param origstream: Output stream for the pairs of original records.
        """
        if not comparisons: return
        from comparison import getvalue
        # File for comparison statistics
        writer = excel.writer(stream)
        writer.writerow(["Score"] + indeces1.keys() + self.keys())
        # File for original records
        record_writer = None
        if origstream is not None:
            record_writer = excel.writer(origstream)
            record_writer.writerow(comparisons.iterkeys().next()[0]._fields)
        # Obtain field-getter for each value comparator
        field1 = [ comparator.field1 for comparator in self.itervalues() ]
        field2 = [ comparator.field2 for comparator in self.itervalues() ]
        # Use dummy classifier scores if None were provided
        if scores is None:
            scores = dict((k,0) for k in comparisons.iterkeys())
        # Write similarity vectors to output
        for (rec1, rec2), score in scores.iteritems():
            weights = comparisons[(rec1,rec2)] # look up comparison vector
            keys1 = [ idx.makekey(rec1) for idx in indeces1.itervalues() ]
            keys2 = [ idx.makekey(rec2) for idx in indeces2.itervalues() ]
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
