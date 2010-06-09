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
    >>> a.count()
    1
    >>> a.compare(compare)
    {(('A', 5.5), ('C', 5.0)): 0.70710678118654757}
    >>> b = Index(makekey, [('D',5.5),('E',4.5)])
    >>> a.count(b)
    3
    >>> a.compare(compare, b)
    {(('C', 5.0), ('D', 5.5)): 0.70710678118654757, (('A', 5.5), ('D', 5.5)): 1.0, (('B', 4.5), ('E', 4.5)): 1.0}
    """
    
    def __init__(self, makekey, records=[]):
        super(Index, self).__init__()
        self.makekey = makekey
        for record in records:
            self.insert(record)
        
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
    
    def count(self, other=None):
        """Return upper bound on the number of comparisons required by this
        index. The actual number of comparison function calls will be lower
        due to caching of comparisons.

        :type: other: :class:`Index` or :keyword:`None`
        :param other: Count comparisons against this index.
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
    
    def search(self, record):
        """Returns a list of records that are indexed under the same keys as
        the provided record."""
        result = []
        for key in self.makekey(record):
            result.extend(self.get(key), [])
        return result
    
    def compare(self, compare, other=None, comparisons=None):
        """Perform comparisons based on the index groups.  By default
        against itself, and optionally against another index.
        
        :type compare: function(`R1`, `R2`) [`float`,...]
        :param compare: Function for comparing a pair of records.
        
        :type other: :class:`Index`
        :param other: Optional second index to compare against.

        :type comparisons: {(`R1`, `R2`):[`float`,...]} 
        :param comparisons: Dict mapping pairs of records to comparisons. For
        single-index we must have `R1` < `R2`, while with two indeces `R1` is
        from `self` while `R2` is from `other`.
        
        :return: Updated comparisons dict.
        """
        if other is None or other is self:
            return self._compare_self(compare, comparisons)
        else:
            return self._compare_other(compare, other, comparisons)
    
    def _compare_self(self, compare, comparisons=None):
        if comparisons is None:
            comparisons = {}
        for indexkey, records in self.iteritems():
            records.sort() # sort the group to ensure a < b
            for j in range(len(records)):
                for i in range(j):
                    # i < j, and sorting means record[i] <= record[j]
                    a,b = records[i], records[j] 
                    # same record indexed under multiple keys!
                    if a is b: 
                        continue
                    # now compare a and b, keeping a <= b
                    if (a,b) not in comparisons:
                        comparisons[(a,b)] = compare(a,b)
        return comparisons
                        
    def _compare_other(self, compare, other, comparisons=None):
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


from compat import OrderedDict as _OrderedDict

class Indices(_OrderedDict):
    """Inserts records into several indeces simultaneously. Behaves as an
    ordered dictionary of Index instances.
    
    :type strategy: [ (`str`, `type`, `function`), ... ]
    :param strategy: List of (index names, index class, key function).
    The index class must support `compare` method, and key function
    must return list of index keys for a record.    

    :type records: [ `tuple`, ... ]
    :param records: List of records to insert into the indeces.

    >>> from dedupe.indexer import Indices, Index
    >>> makekey = lambda r: [int(r[1])]
    >>> makekey(('A',3.5))
    [3]
    >>> strategy = [ ("MyIndex", Index, makekey) ]
    >>> records1 = [('A',5.5),('B',4.5),('C',5.25)]
    >>> records2 = [('D',5.5),('E',4.5),('F',5.25)]
    >>> Indices(strategy, records1)
    OrderedDict([('MyIndex', {4: [('B', 4.5)], 5: [('A', 5.5), ('C', 5.25)]})])
    """

    def __init__(self, strategy, records=[]):
        super(Indices, self).__init__(
            (name, idxtype(keyfunc, records)) for name, idxtype, keyfunc in strategy)
            
    def insert(self, record):
        """Insert a record into each :class:`Index`."""
        for index in self.itervalues():
            index.insert(record)
                        
    def compare(self, simfunc, other=None):
        """Compute similarities of indexed pairs of records.  
        
        :type simfunc: func(`R`, `R`) (`float`,...)
        :param simfunc: takes a pair of records and returns a similarity vector.
        
        :type other: :class:`Indeces`
        :param other: Compare records against another set of Indeces (default
        is to compare records against themselves).
        
        :rtype: {(R,R):(float,...)}
        :return: mapping from pairs of records similarity vectors.
        """
        comparisons = {}
        if other is None or other is self:
            for index in indices.itervalues():
                index.compare(simfunc, None, comparisons)
        else:
            for index1, index2 in zip(self.itervalues(), other.itervalues()):
                if type(index1) is not type(index2):
                    raise TypeError(
                        "Indeces of type %s and type %s are incompatible" % 
                        (type(index1), type(index2)))
                index1.compare(simfunc, index2, comparisons)
        return comparisons
