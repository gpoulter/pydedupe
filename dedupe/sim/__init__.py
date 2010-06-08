"""
Compare values, fields, and records for similarity
==================================================

.. moduleauthor:: Graham Poulter
"""

import dale, geo, levenshtein

try:
    from dedupe.compat import OrderedDict as _OrderedDict
except:
    from ..compat import OrderedDict as _OrderedDict

class Scale:
    """Re-scale the return values of similarity function so that a sub-range 
    of its is mapped onto the 0.0 to 1.0 result.  
    
    :note: The default `low`=0.0 and `high`=1.0 do nothing. Higher values of
    `low` make stricter comparisons, and lower values of `high` make more
    lenient comparisons.
    
    @ivar similarity: A similarity function, takes two records and returns 
    a float in the range 0.0 to 1.0.
    @ivar low: Raw similarity values below `low` are scaled to 0.0.  
    @ivar high: Raw similarity values above `high` are scaled to 1.0
    @ivar missing: Return `missing` when `similarity` returns `None` (defaults to `None`).
    @ivar test: Optional function to check for bad values.  If `a` and `b` pass
    the test then return `similarity(a,b)`, otherwise return `missing`.
    
    >>> from dedupe import sim
    >>> simfunc = lambda a,b: 2**-abs(a-b) 
    >>> isnum = lambda x: isinstance(x,int) or isinstance(x,float)
    >>> simfunc(1,2)
    0.5
    >>> sim.Scale(simfunc)(1,2)
    0.5
    >>> sim.Scale(simfunc, low=0.6)(1,2)
    0.0
    >>> sim.Scale(simfunc, high=0.4)(1,2)
    1.0
    >>> sim.Scale(simfunc, low=0.4, high=0.6)(1,2)
    0.5
    >>> print sim.Scale(simfunc, test=isnum)("blah",2)
    None
    """
    
    def __init__(self, similarity, low=0.0, high=1.0, missing=None, test=None):
        if not (0.0 <= low <= 1.0 and 0.0 <= high <= 1.0 and low < high):
            raise ValueError("low: %s, high: %s" % (str(low),str(high)))
        self.similarity = similarity 
        self.low = low
        self.high = high
        self.missing = missing
        self.test = test
        
    def __call__(self, a, b):
        if self.test and not (self.test(a) and self.test(b)):
            return self.missing
        v = self.similarity(a,b)
        if v is None:
            return self.missing
        if v <= self.low:
            return 0.0
        if  v >= self.high:
            return 1.0
        return (v-self.low)/(self.high-self.low)


class Field(object):
    """Computes the similarity of a pair of records on a specific field.
    
    :type compare: callable(`V`, `V`) :class:`float`
    :param compare: Returns similarity of a pair of encoded field values.

    :type field1: callable(`R`) -> `T1`
    :param field1: Gets field value from first record.
    :type encode1: callable(`T1`) `V`
    :param encode1: Encodes field value from first record (default=`lambda x:x`)
    
    :type field2: callable(`R`) -> `T1`
    :param field2: Gets field value from the second record (default=`field1`)
    :type encode2: callable(`T1`) `V`
    :param encode2: Encodes field value from the second record (default=`encode1`)

    >>> from dedupe import sim
    >>> from dedupe.get import item
    >>> # define some 'similarity of numbers' measure
    >>> similarity = lambda x,y: 2**-abs(x-y)
    >>> similarity(1,2)
    0.5
    >>> Field(similarity, item(1), float)(('A','1'),('B','2'))
    0.5
    >>> fsim = Field(similarity, field1=item(0), encode1=lambda x:x, field2=item(1), encode2=float)
    >>> fsim((1,'A'),('B','2'))
    0.5
    """
    
    def __init__(self, compare, field1, encode1=None, field2=None, encode2=None):
        from dedupe.get import getter 
        self.compare = compare
        self.field1 = getter(field1)
        self.encode1 = encode1 if encode1 else lambda x:x
        self.field2 = getter(field2) if field2 else self.field1
        self.encode2 = encode2 if encode2 else self.encode1

    def __call__(self, record1, record2):
        """Returns the similarity of `record1` and `record2` on this field."""
        return self.compare(
            self.encode1(self.field1(record1)), 
            self.encode2(self.field2(record2)))


class Average(Field):
    """Computes the average similarity of a pair of records on 
    a multi-valued field.
      
    It computes the average by considering each field value from
    the record with the fewest values and accumulating the
    greatest similarity against the values in the other record. 
    If the shorter field is a subset of the longer field, 
    the similarity should be 1.0.
    
    :type compare: callable(`V`, `V`) :class:`float`
    :param compare: Returns similarity of a pair of encoded field values.
    :type field1: function(`R`) [`T1`,...]
    :param field1: Iterates over multi-values of the field.
    :type field2: function(`R`) [`T2`,...]
    :param field2: Iterates over multi-values of the field (default=`field1`).
    :type encode1: function(`T1`) `V`
    :param encode1: Encode of field1 values.
    :type encode2: function(`T2`) `V`
    :param encode2: Encoder of field2 value (default=`encode1`).
    :rtype: callable(`R1`, `R2`) float
    :return: Computer of average similarity of records `R1` and `R2` for values of the field.
    
    >>> # define an exponential 'similarity of numbers' measure
    >>> similarity = lambda x,y: 2.0**(-abs(x-y))
    >>> field = lambda r: set([r[0],r[2]])
    >>> from dedupe import sim
    >>> sim.Average(similarity, field, float)((1,'A','1'),(-2,'B',2))
    0.5
    >>> field = lambda r: set(r[1].split(';'))
    >>> sim.Average(similarity, field, float)(('A','0;1'),('B','1;2'))
    0.75
    >>> sim.Average(similarity, field, float)(('A','0;1;2'),('B','0;1;2;3;4'))
    1.0
    """
    
    def __call__(self, record1, record2):
        """Return the average similarity of `record1` and `record2` on 
        this multi-valued field"""
        f1 = set(self.encode1(v1) for v1 in self.field1(record1))
        f2 = set(self.encode2(v2) for v2 in self.field2(record2))
        f1, f2 = sorted([f1, f2], key=len) # short set, long set
        # Missing value check
        if len(f1) == 0 or len(f2) == 0:
            return self.compare(None,None) 
        total = 0.0
        for v1 in f1:
            best = 0.0
            for v2 in f2:
                comp = self.compare(v1,v2)
                best = max(best, comp)
            total += best # score of most similar item in the long set
        return total / len(f1)


class Maximum(Field):
    """Computes the maximum similarity of a pair of records on a 
    multi-valued field.
    
    :type compare: callable(`V`, `V`) :class:`float`
    :param compare: Returns similarity of a pair of encoded field values.
    :type field1: callable(`R`) [`T1`,...]
    :param field1: Returns a list of values for the field.
    :type field2: callable(`R`) [`T2`,...]
    :param field2: Returns a list of values for the field. (default=`field1`).
    :type encode1: function(`T1`) `V`
    :param encode1: Encodes each field1 value for comparison.
    :type encode2: function(`T2`) `V`
    :param encode2: Encodes each field1 value for comparison.(default=`encode1`).

    >>> # define an exponential 'similarity of numbers' measure
    >>> similarity = lambda x,y: 2.0**(-abs(x-y))
    >>> field = lambda r: set([r[0],r[2]])
    >>> from dedupe import sim
    >>> sim.Maximum(similarity, field, float)((0,'A','1'),(2,'B',2))
    0.5
    >>> field = lambda r: set(r[1].split(';'))
    >>> sim.Maximum(similarity, field, float)(('A','0;1;2'),('B','3;4;5'))
    0.5
    """
    
    def __call__(self, record1, record2):
        """Return the maximum similarity of `record1` and `record2` on
        this multi-valued field."""
        f1 = set(self.encode1(v1) for v1 in self.field1(record1))
        f2 = set(self.encode2(v2) for v2 in self.field2(record2))
        # Missing value check
        if len(f1) == 0 or len(f2) == 0:
            return self.compare(None,None) 
        best = 0.0
        for v1 in f1:
            for v2 in f2:
                comp = self.compare(v1,v2)
                best = max(best, comp)
        return best


class Record(_OrderedDict):
    """Returns a vector of field value similarities between two records.

    :type \*simfuncs: [(:class:`str`, :class:`Field`), ...]
    :param \*simfuncs: Pairs of (field name, similarity function) used
    to compute the tuple of similarities.
    
    :ivar Similarity: namedtuple class for the similarity of a pair of records,
    with field names corresponding to `simfuncs`.
    
    :rtype: function(`R`, `R`) :class:`Similarity` 
    :return: Takes two records and returns a `Similarity` tuple.

    >>> # define a 'similarity of numbers' measure
    >>> similarity = lambda x,y: 2.0**(-abs(x-y))
    >>> from dedupe import sim 
    >>> vcomp1 = sim.Field(similarity, 1, float) # field 1 from record
    >>> vcomp2 = sim.Field(similarity, 2, float) # field 2 from field
    >>> rcomp = sim.Record(("V1",vcomp1),("V2",vcomp2))
    >>> rcomp(('A',1,1), ('B',2,4))
    Similarity(V1=0.5, V2=0.125)
    """
    
    def __init__(self, *simfuncs):
        super(Record, self).__init__(simfuncs)
        import dedupe.compat as c
        self.Similarity = c.namedtuple("Similarity", self.keys())

    def __call__(self, A, B):
        return self.Similarity._make(
            fieldsimilarity(A, B) for fieldsimilarity in self.itervalues())
