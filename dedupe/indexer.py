"""
:mod:`indexer` -- Inverted index of records
===========================================

An inverted index lists records sharing an index key. By only comparing
pairs of records that share index keys the total number of comparisons
can be vastly reduced over the case of comparing all pairs of records.

.. module:: indexer
   :synopsis: Index records and carry out pairwise comparisons.
.. moduleauthor:: Graham Poulter

"""

from __future__ import with_statement

import logging
from compat import namedtuple, OrderedDict
import excel

class Index(dict):
    """Mapping from index key to records.
    
    :type makekey: function(record) [key,...]
    :param makekey: Generates the index keys for the record.    
    """
    
    def __init__(self, makekey):
        super(Index, self).__init__()
        self.makekey = makekey
        
    def insert(self, record):
        """Insert a record into the index.

        :type record: :class:`namedtuple`
        :param record: The record object to index.
        :rtype: [key,...]
        :return: Keys under which the record was inserted.
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
        """Upper bound on the number of comparisons required by this index.
        
        .. note:: caching of comparisons results will generally mean fewer
           actual calls to the comparison function than.

        :type: other: :class:`Index` or :keyword:`None`
        :param other: Count comparisons against this index.
        :rtype: int
        :return: Most pairwise comparisons that need to be made.
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
        """Statistics about the average and largest block sizes
        
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
        """Write index in CSV format.
        :type stream: binary stream writer
        :param stream: Destination for CSV text.
        """
        writer = excel.writer(stream)
        for indexkey, rows in self.iteritems():
            for row in rows:
                writer.writerow((indexkey,) + row)


class Indeces(OrderedDict):
    """Represents a sever Index instances as an ordered dictionary.

    :type indeces: (string, :class:`Index`)
    :param indeces: Use these named indeces.
    """

    def __init__(self, *indeces):
        OrderedDict.__init__(self)
        for key, value in indeces:
            self[key] = value
    
    def insert(self, records):
        """Insert records into each :class:`Index`."""
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
        """Write the indeces in CSV format to these paths."""
        for indexname, index in self.iteritems():
            with open(basepath + indexname + ".csv", "w") as stream:
                index.write_csv(stream)



class RecordComparator(OrderedDict):
    """Returns a vector of field value similarities between two records.

    :type comparators: [(string,:class:`comparison.Value`),...]
    :param comparators: Named, ordered field comparisons.
    
    :type Weights: :class:`namedtuple` (float,...)
    :ivar Weights: type of similarity vector between records\
      with field names corresponding to the names in `comparators`.
    
    :rtype: callable(R,R) :class:`Weights`
    :return: Compare two records using each value comparator in turn, giving\
      a vector of corresponding named similarity values.    
    """
    
    def __init__(self, *comparators):
        super(RecordComparator, self).__init__(comparators)
        self.Weights = namedtuple("Weights", self.keys())

    def __call__(self, A, B):
        return self.Weights._make(
            comparator(A, B) for comparator in self.itervalues())
    
    def allpairs(self, records):
        """Return comparisons for all distinct pairs of records.
        
        :type records: [R,...]
        :param records: records to compare
        :rtype: {(R,R):[float,...],...}
        :return: Similarity vectors for ordered pairs of compared records.
        """
        comparisons = {}
        for i in range(len(records)):
            for j in range(i):
                rec1, rec2 = records[i], records[j]
                assert rec1[0] != rec2[0]
                pair = tuple(sorted([rec1,rec2], key=lambda x:x[0]))
                if pair not in comparisons:
                    comparisons[pair] = self(rec1, rec2)
        return comparisons

    def dedupe(self, indeces):
        """Return comparisons against self for indexed records.
        
        :type indeces: :class:`Indeces`, {str:{obj:[R,...],...},...}
        :param indeces: indexed left-hand records
        :rtype: {(R,R):[float,...],...}
        :return: Similarity vectors for ordered pairs of compared records.
        """
        comparisons = {} # Map from (record1,record2) to L{Weights}
        for index in indeces.itervalues():
            index.dedupe(self, comparisons)
        return comparisons
    

    def link(self, indeces1, indeces2):
        """Return comparisons between two sets of indexed records.

        :type indeces1: :class:`Indeces`, {str:{obj:[R,...],...},...}
        :param indeces1: indexed left-hand records
        :type indeces2: :class:`Indeces`, {str:{obj:[R,...],...},...}
        :param indeces2: indexed right-hand records
        :rtype: {(R,R):[float,...],...}
        :return: Similarity vectors for ordered pairs of compared records.
        """
        assert indeces1 is not indeces2 # Must be different!
        comparisons = {}
        for index1, index2 in zip(indeces1.itervalues(), indeces2.itervalues()):
            index1.link(index2, self, comparisons)
        return comparisons


    def write_comparisons(self, indeces1, indeces2, comparisons, scores, stream, origstream=None):
        """Write pairs of compared records, together with index keys and 
        field comparison weights.  Inspection shows which index keys matched,
        and the field-by-field similarity.
        
        :type indeces1: :class:`Indeces`, {str:{obj:[R,...],...},...}
        :param indeces1: indexed left-hand records
        :type indeces2: :class:`Indeces`, {str:{obj:[R,...],...},...}
        :param indeces2: indexed right-hand records\
           (provide same object as indeces1 for self-linkage)

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
