"""
Index records before comparing them
===================================

An Index groups records together so that only pairs of records in the same
group need to be compared, greatly reducing the number of record pairs to
analyse.   For example, indexing on phone number and phonetic name will compare
only records that have the same phone number, or the same phonetic version of
the name.

.. moduleauthor:: Graham Poulter
"""

from __future__ import with_statement

from compat import OrderedDict as _OrderedDict
import logging
import excel

class Index(dict):
    """Mapping from index key to records.
    
    :type makekey: function(`R`) [`K`,...]
    :param makekey: Generates the index keys for the record.
    
    :type records: [`R`,...]
    :param records: Initial records to load into the index.
    
    >>> makekey = lambda r: [int(r[1])]
    >>> makekey(('A',3.5))
    [3]
    >>> compare = lambda x,y: 2**-abs(float(x[1])-float(y[1]))
    >>> compare(('A','5.5'),('B','4.5'))
    0.5
    >>> from dedupe.indexer import Index
    >>> a = Index(makekey, [('A',5.5),('B',4.5),('C',5.0)])
    >>> a.count_comparisons()
    1
    >>> a.link_within(compare)
    {(('A', 5.5), ('C', 5.0)): 0.70710678118654757}
    >>> b = Index(makekey, [('D',5.5),('E',4.5)])
    >>> a.count_comparisons(b)
    3
    >>> a.link_between(compare, b)
    {(('C', 5.0), ('D', 5.5)): 0.70710678118654757, (('A', 5.5), ('D', 5.5)): 1.0, (('B', 4.5), ('E', 4.5)): 1.0}
    """
    
    def __init__(self, makekey, records=None):
        super(Index, self).__init__()
        self.makekey = makekey
        if records:
            self.insertmany(records)
        
    def insert(self, record):
        """Insert a record into the index.

        :type record: :class:`namedtuple` or other record.
        :param record: The record object to index.
        :rtype: [`K`,...]
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
        :rtype: :class:`int`
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
        
        :type compare: function(`R1`, `R2`) [:class:`float`,...]
        :param compare: how to compare each pair of records.
        
        :type comparisons: {(`R1`, `R2`):[:class:`float`,...]} where `R1` < `R2`
        :param comparisons: Cache of comparisons of ordered-pairs of records.
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
        
        :type compare: function(`R1`, `R2`) [:class:`float`,...]
        :param compare: how to compare each pair of records.
        
        :type other: :class:`Index`
        :param other: link records from this index to the `other` index.

        :type comparisons: {(`R1`, `R2`):[:class:`float`,...]} where `R1` < `R2`
        :param comparisons: Cache of comparisons of ordered-pairs of records.
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


class Indices(_OrderedDict):
    """Represents a sever Index instances as an ordered dictionary.

    :type indices: (:class:`str`, :class:`Index`), ...
    :param indices: Named indices in which to insert records.
    
    >>> makekey = lambda r: [int(r[1])]
    >>> makekey(('A',3.5))
    [3]
    >>> from dedupe.indexer import Indices, Index
    >>> a = Indices(("IntValue",Index(makekey,[('A',5.5),('B',4.5),('C',5.25)])))
    >>> a
    OrderedDict([('IntValue', {4: [('B', 4.5)], 5: [('A', 5.5), ('C', 5.25)]})])
    >>> a.clone([('D',5.5),('E',4.5),('F',5.25)])
    OrderedDict([('IntValue', {4: [('E', 4.5)], 5: [('D', 5.5), ('F', 5.25)]})])
    """

    def __init__(self, *indices):
        _OrderedDict.__init__(self)
        for key, value in indices:
            self[key] = value
            
    def clone(self, records=None):
        """Return a new :class:`Indices` with same layout as this one,
        and optionally loaded with provided `records`."""
        indices = Indices(*[(n,Index(idx.makekey)) for n,idx in self.iteritems()])
        if records:
            indices.insertmany(records)
        return indices
    
    def insert(self, record):
        """Insert a record into each :class:`Index`."""
        for index in self.itervalues():
            index.insert(record)
            
    def insertmany(self, records):
        """Insert records into each :class:`Index`."""
        for record in records:
            self.insert(record)
