"""Inverted index of records, and comparator of records that can use
an inverted index to reduce the required number of comparisons.

Record ID is always assumed to be the first field of a record.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

from __future__ import with_statement

import logging
from compat import namedtuple, OrderedDict
import namedcsv

def getfield(record, field):
    """Retrieve a field from a record. The field may be specified with an
    integer index (for tuple records), string attribute names (for record objects), 
    or a function (for computed fields)).
    
    @return: Any object representing the field value. Most often a string
    value of some field, but may be an integer, a set of strings, or a
    coordinate pair, etc.
    """
    if isinstance(field, str):
        return record.__getattribute__(field)
    elif isinstance(field, int):
        return record[field]
    elif hasattr(field, "__call__"):
        return field(record)
    else:
        raise ValueError("Could not locate field %s in %s", str(field), str(record))
    

class Index(dict):
    """A dictionary mapping index keys to a list of records that were
    inserted with that index key.
    
    The makekey function takes a record and returns a list of keys
    under which the record should be indexed.  For something like soundex
    there would only be one key in the list, but double-metaphone might
    return two keys, and n-gram combinations always return several keys."""
    
    def __init__(self, makekey):
        """Parameterise the Index. 
        
        @param makekey: Function of the record tuple that returns
        list or tuple of index keys under which the record should be inserted. 
        """
        super(Index, self).__init__()
        self.makekey = makekey
        
    def insert(self, record):
        """Index a record by its keys. Only indexes keys for which bool(key)
        evaluates to True, meaning that keys such as False, 0, "", None are
        not included in the index.
        
        @param record: The record object to index.
        @return: The sequence of keys under which the record was inserted.
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

        @param other: Index instance to compare this one against, to count
        linkage comparisons instead of dedupe comparisons.
        
        @return: Maximum pairwise comparisons that need to be made, if each
        comparison is distinct. Fewer comparisons take place if records appear
        in multiple index blocks, due to caching.
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
        
        @param prefix: Print before the log message.
        @param log: Logging object to use.
        """
        if log is None: log = logging.getLogger()
        nrecords = sum(len(recs) for recs in self.itervalues())
        biggroup = max(len(recs) for recs in self.itervalues())
        nkeys = len(self)
        log.info(prefix + "%d records in %d blocks. Largest block: %d, Average block: %.2f",
                 nrecords, nkeys, biggroup, float(nrecords)/nkeys)
        
    def dedupe(self, compare, comparisons=None):
        """Perform dedupe comparisons on the index.  Note that this sorts
        the lists of records in each index key to ensure that rec1<rec2 
        in each resulting comparison tuple.
        
        @param compare: Function of two records returning a similarity vector
        such as [0.3,0.8,1.0,...].
        
        @param comparisons: Cache of comparisons, mapping (rec1,rec2) 
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
        
        @param other: Index object against which to perform linkage comparison.
        
        @param compare: Function of two records returning a similarity vector
        such as [0.3,0.8,1.0,...].
        
        @param comparisons: Cache of comparisons mapping (rec1,rec2) to
        similarity vector. Inserted pairs will have rec1 from self and rec2
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
        writer = namedcsv.uwriter(stream)
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
        
        @param other: L{Indeces} object, being an ordered dictionary of Index
        objects.  None to log statistics for just this index.
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

class ValueComparator(object):
    """Defines a callable comparison of a pair of records on a defined field.
    
    @ivar comparevalues: Function to compare the computed, encoded field values.
    @ivar field1: Field specifier applied to the first record.
    @ivar encode1: Function to encode field values from the first record.
    @ivar field2: Field specifier applied to the second record (default is field1).
    @ivar encode2: Function to encode field values from second record (default is encode1).
    
    @note: The L{field1} and L{field2} specifiers may be an integer index into the record, 
    a string key or attribute to look up in the record, or in the most general
    case a function applied to the record to compute a field value.
    
    @note: The L{encode1} and L{encode2} functions transform the retrieved field values
    just prior to comparison, for example to remove spaces and fold case.  Each
    accepts one paramenter of the type returned by the corresponding field
    parameter, and returns a value suitable for comparevalues.
    
    @note: The L{comparevalues} function takes two parameters, of the
    value types returned by encode1 and encode2 respectively. 
    """
    
    def __init__(self, comparevalues, field1, encode1=lambda x:x, field2=None, encode2=None):
        """Initialise field comparison object"""
        self.comparevalues = comparevalues
        self.field1 = field1
        self.encode1 = encode1
        self.field2 = field2 or field1
        self.encode2 = encode2 or encode1

    def __call__(self, record1, record2):
        """Compare the two records on the defined fields."""
        return self.comparevalues(
            self.encode1(getfield(record1, self.field1)), 
            self.encode2(getfield(record2, self.field2)))

    
class SetComparatorAvg(ValueComparator):
    """Compare the similarity of two sets of values. Set of values obtained 
    either from splitting a single column, or combining multiple columns.
    
    The similarity is from looping over the smaller set of values, finding the
    best match in the larger set, and taking the average by dividing the total
    by the length of the smaller set. If each item in the smaller set has a
    perfect match in the larger, the similarity is 1.0.
    
    @ivar field1, field2: Take a record and return a set of values (computed
    field).
    
    @ivar encode1, encode2: Apply these functions each value in the sets
    obtained from L{field1} and L{field2}, just prior to comparing the sets.
    """
    
    def __call__(self, record1, record2):
        """Compare two records on a set-of-values field."""
        f1 = set(self.encode1(v1) for v1 in self.field1(record1))
        f2 = set(self.encode2(v2) for v2 in self.field2(record2))
        f1, f2 = sorted([f1, f2], key=len) # short set, long set
        # Missing value check
        if len(f1) == 0 or len(f2) == 0:
            return self.comparevalues(None,None) 
        total = 0.0
        for v1 in f1:
            best = 0.0
            for v2 in f2:
                comp = self.comparevalues(v1,v2)
                best = max(best, comp)
            total += best # score of most similar item in the long set
        return total / len(f1)
    
class SetComparatorMax(ValueComparator):
    """Compare the similarity of two sets of values. Set of values obtained 
    either from splitting a single column, or combining multiple columns.
    
    The similarity is the maximum of the pair-wise comparisons between the two
    sets. One perfectly matching pair of values between the two sets returns a
    similarity of 1.0.
    
    @ivar field1, field2: Take a record and return a set of values (computed
    field).
    
    @ivar encode1, encode2: Apply these functions each value in the sets
    obtained from L{field1} and L{field2}, just prior to comparing the sets.
    """
    
    def __call__(self, record1, record2):
        """Compare two records on a set-of-values field."""
        f1 = set(self.encode1(v1) for v1 in self.field1(record1))
        f2 = set(self.encode2(v2) for v2 in self.field2(record2))
        # Missing value check
        if len(f1) == 0 or len(f2) == 0:
            return self.comparevalues(None,None) 
        best = 0.0
        for v1 in f1:
            for v2 in f2:
                comp = self.comparevalues(v1,v2)
                best = max(best, comp)
        return best

class RecordComparator(OrderedDict):
    """Ordered dictionary mapping comparison weight fields to field comparison
    functions. The compare methods then compare pairs of records using those
    functions, returning namedtuple vectors corresponding to the
    results of each comparison function applied to the record.
    
    @ivar Weights: Namedtuple type of the similarity vector, with field names
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

        @param records: List of record namedtuples.

        @return: Mapping pairs (record1, record2) to L{Weights} similarity vector.
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
        
        @return: Map from compared (record1,record2) to L{Weights} vector.
        Each compared tuple is lexicographically ordered (record1 < record2).
        """
        comparisons = {} # Map from (record1,record2) to L{Weights}
        for index in indeces.itervalues():
            index.dedupe(self.compare, comparisons)
        return comparisons
    

    def link(self, indeces1, indeces2):
        """Compare two sets of records using indexing to reduce number of comparisons.
        
        @param indeces1: List of L{Index} objects for first dataset.
        
        @param indeces2: List of corresponding L{Index} objects for second
        data set.

        @return: Map from (rec1,rec2) to comparison weights. The tuple has
        rec1 from indeces1 and rec2 from indeces2, unlike
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
        
        @param indeces1: L{Indeces} for the left-hand records
        
        @param indeces2: L{Indeces} for the right-hand records for linkage.
        Use the same as indeces1 in the case of dedupe.

        @param comparisons: Map from (rec1,rec2) to similarity vector.

        @param scores: Map from (rec1,rec2) to classifier score.  Only output
        the pairs found in scores.  If None, output all without classifier score.
        
        @param stream: Output stream for the detailed comparison results.
        
        @param origstream: Output stream for the pairs of original records.
        """
        if not comparisons: return
        # File for comparison statistics
        writer = namedcsv.uwriter(stream)
        writer.writerow(["Score"] + indeces1.keys() + self.keys())
        # File for original records
        record_writer = None
        if origstream is not None:
            record_writer = namedcsv.uwriter(origstream)
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
            writer.writerow([""] + [";".join(x) for x in keys1] + [ str(getfield(rec1,f)) for f in field1 ])
            writer.writerow([""] + [";".join(x) for x in keys2] + [ str(getfield(rec2,f)) for f in field2 ])
            # Tuple of booleans indicating whether index keys are equal
            idxmatch = [ bool(set(k1).intersection(set(k2))) if 
                         (k1 is not None and k2 is not None) else ""
                         for k1,k2 in zip(keys1,keys2) ]
            weightrow = [score] + idxmatch + list(weights)
            writer.writerow(str(x) for x in weightrow)
            if record_writer:
                record_writer.writerow(rec1)
                record_writer.writerow(rec2)
            
            
    
