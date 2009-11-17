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

from compat import OrderedDict
import logging
import excel

class Index(dict):
    """Mapping from index key to records.
    
    :type makekey: function(record) [key,...]
    :param makekey: Generates the index keys for the record.
    
    >>> makekey = lambda r: [int(r[1])]
    >>> compare = lambda x,y: float(int(x[1])==int(y[1]))
    >>> makekey(('A',3.5))
    [3]
    >>> a = Index(makekey)
    >>> a.insertmany([('A',5.5),('B',4.5),('C',5.25)])
    >>> a.count_comparisons()
    1
    >>> a.link_within(compare)
    {(('A', 5.5), ('C', 5.25)): 1.0}
    >>> b = Index(makekey)
    >>> b.insertmany([('D',5.5),('E',4.5)])
    >>> a.count_comparisons(b)
    3
    >>> a.link_between(compare, b)
    {(('C', 5.25), ('D', 5.5)): 1.0, (('A', 5.5), ('D', 5.5)): 1.0, (('B', 4.5), ('E', 4.5)): 1.0}
    """
    
    def __init__(self, makekey):
        super(Index, self).__init__()
        self.makekey = makekey
        
    def insert(self, record):
        """Insert a record into the index.

        :type record: :class:`namedtuple` or other record.
        :param record: The record object to index.
        :rtype: [key,...]
        :return: Keys under which the record was inserted.
        """
        keys = self.makekey(record)
        for key in keys:
            if key is None or key == "":
                raise ValueError("Empty index key in %s" % repr(keys))
            recordsforkey = self.setdefault(key, list())
            recordsforkey.append(record)
        return keys
    
    def insertmany(self, records):
        """Insert records into the index."""
        for record in records:
            self.insert(record)
    
    def count_comparisons(self, other=None):
        """Upper bound on the number of comparisons required by this index.
        
        .. note:: comparisons are cached so the actual number of calls to the
           comparison function will in general be less than this.

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
    
    def link_within(self, compare, comparisons=None):
        """Perform dedupe comparisons on the index.  Note that this sorts
        the lists of records in each index key to ensure that rec1<rec2 
        in each resulting comparison tuple.
        
        :type compare: function(R,R) [float,...]
        :param compare: How to compare the records.
        
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
                        
    def link_between(self, compare, other, comparisons=None):
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


class Indices(OrderedDict):
    """Represents a sever Index instances as an ordered dictionary.

    :type indices: (string, :class:`Index`)
    :param indices: Named indices in which to insert records.
    
    >>> makekey = lambda r: [int(r[1])]
    >>> makekey(('A',3.5))
    [3]
    >>> a = Indices(("IntValue",Index(makekey)))
    >>> a.insertmany([('A',5.5),('B',4.5),('C',5.25)])
    >>> a
    OrderedDict([('IntValue', {4: [('B', 4.5)], 5: [('A', 5.5), ('C', 5.25)]})])
    >>> b = a.clone()
    >>> b.insertmany([('D',5.5),('E',4.5),('F',5.25)])
    >>> b
    OrderedDict([('IntValue', {4: [('E', 4.5)], 5: [('D', 5.5), ('F', 5.25)]})])
    """

    def __init__(self, *indices):
        OrderedDict.__init__(self)
        for key, value in indices:
            self[key] = value
            
    def clone(self):
        """Return a new :class:`Indeces` with same layout as this one."""
        return Indices(*[(n,Index(idx.makekey)) for n,idx in self.iteritems()])
    
    def insert(self, record):
        """Insert a record into each :class:`Index`."""
        for index in self.itervalues():
            index.insert(record)
            
    def insertmany(self, records):
        """Insert records into each :class:`Index`."""
        for record in records:
            self.insert(record)