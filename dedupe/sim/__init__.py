"""
Compare values, fields, and records for similarity
==================================================

.. moduleauthor:: Graham Poulter
"""

import dale, geo, levenshtein

try:
    from compat import OrderedDict as _OrderedDict
except:
    from ..compat import OrderedDict as _OrderedDict

def fallback(main, backup, row):
    """Attempt to use main attribute of row, but fall back to a backup attribute
    if the main one is empty."""
    val = ""
    if hasattr(row, main):
        val = getattr(row, main)
    if not val.strip() and hasattr(row, backup):
        val = getattr(row, backup)
    return val

def getvalue(record, field):
    """Retrieve value of a field from a record by any means.
    
    :type record: :class:`namedtuple` or :class:`tuple`
    :param record: record from which to retrive field value
    :type field: :class:`str`, :class:`int`, or function(`R`)
    :param field: field specifier, to attempt R.field, R[field] and field(R)
    :rtype: any field value (string, number, or collection of strings)
    :return: Value of `field` on `record`
    
    >>> from collections import namedtuple
    >>> from dedupe import sim
    >>> sim.getvalue(namedtuple('Record','A B')(1,2), 'A')
    1
    >>> sim.getvalue(['a','b'], 0)
    'a'
    >>> sim.getvalue({'A':'B'}, lambda r: r['A'])
    'B'
    """
    if isinstance(field, str):
        return record.__getattribute__(field)
    elif isinstance(field, int):
        return record[field]
    elif hasattr(field, "__call__"):
        return field(record)
    else:
        raise ValueError("Could not locate field %s in %s", str(field), str(record))

def multivalue(sep, *fields):
    """Return a function that combines delimited fields as a virtual
    multi-value field.

    :type sep: :class:`str`
    :param sep: Delimiter to split fields into multiple values
    :type fields: Field specifiers for :func:`getvalue`
    :param fields: Fields whose values are to be combined.
    :rtype: [`V`, ...]
    :return: The virtual-field values

    >>> from dedupe import sim
    >>> sim.multivalue(";", 0, 1)(['1;2;3','4;5'])
    ['1', '2', '3', '4', '5']
    """
    def field_splitter(record):
        """Create a multi-value from multiple delimited fields %s using delimiter %s"""
        result = []
        for field in fields:
            value = getvalue(record, field)
            values = [value] if sep is None else value.split(sep)
            result += [s.strip() for s in values if s.strip()]
        return result
    field_splitter.__doc__ %= ",".join([str(x) for x in fields]), sep
    return field_splitter

def combine(*fields):
    """Return a function that combines single-value fields into a virtual
    multi-valued field.
    
    :type fields: Field specifiers for :func:`getvalue`
    :param fields: Fields whose values are to be combined.
    :rtype: [`V`, ...]
    :return: The virtual-field values
    
    >>> from dedupe import sim
    >>> sim.combine(0, 2, 3)(['A','B','C','D','E'])
    ['A', 'C', 'D']
    """
    return multivalue(None, *fields)    


class ValueSim(object):
    """Defines a callable comparison of a pair of records on a defined field.
    
    :type comparevalues: function(`V`, `V`) :class:`float`
    :param comparevalues: Compares the encoded values and returns similarity.
    :type field1: :class:`str`, :class:`int`, or function(`R`)
    :param field1: the :func:`getvalue` specifier for the first record 
    :type encode1: function(`T1`) `V`
    :param encode1: Encoder of field1 values.
    :type field2: :class:`str`, :class:`int`, or function(`R`)
    :param field2: the :func:`getvalue` specifier for the second record 
    :type encode2: function(`T2`) `V`
    :param encode2: Encoder of field2 value (default=`encode1`).
    :rtype: callable(`R1`,`R2`) :class:`float`
    :return: Computes similarity of records `R1` and `R2` on the defined field.

    >>> from dedupe.sim import ValueSim
    >>> # define some 'similarity of numbers' measure
    >>> similarity = lambda x,y: 2.0**(-abs(x-y))
    >>> ValueSim(similarity, 1, float)(('A',1),('B',1))
    1.0
    >>> ValueSim(similarity, 1, float)(('A','1'),('B','2'))
    0.5
    >>> ValueSim(similarity, 0, None, 1, float)((1,'A'),('B','2'))
    0.5
    """
    
    def __init__(self, comparevalues, field1, encode1=None, field2=None, encode2=None):
        self.comparevalues = comparevalues
        self.field1 = field1
        self.encode1 = encode1 if encode1 else lambda x:x
        self.field2 = field2 or field1
        self.encode2 = encode2 if encode2 else self.encode1

    def __call__(self, record1, record2):
        """Compare the two records on the defined fields."""
        return self.comparevalues(
            self.encode1(getvalue(record1, self.field1)), 
            self.encode2(getvalue(record2, self.field2)))

    
class ValueSimAvg(ValueSim):
    """Return average similarity of multi-valued fields.
    
    The average is obtained by looping over the shorter field, and totalling
    the best similaritois to values of the longer field, then dividing by
    the length of the shorter field.  That means that if the shorter field
    is a subset of the longer field, the similarity should work out to 1.0.
    
    :type comparevalues: function(`V`, `V`) :class:`float`
    :param comparevalues: Compares the encoded values and returns similarity.
    :type field1: function(`R`) [`T1`,...]
    :param field1: Iterates over multi-values of the field.
    :type field2: function(`R`) [`T2`,...]
    :param field2: Iterates over multi-values of the field (default=`field1`).
    :type encode1: function(`T1`) `V`
    :param encode1: Encoder of field1 values.
    :type encode2: function(`T2`) `V`
    :param encode2: Encoder of field2 value (default=`encode1`).
    :rtype: callable(`R1`, `R2`) float
    :return: Computer of average similarity of records `R1` and `R2` for values of the field.
    
    >>> # define an exponential 'similarity of numbers' measure
    >>> similarity = lambda x,y: 2.0**(-abs(x-y))
    >>> field = lambda r: set([r[0],r[2]])
    >>> from dedupe.sim import ValueSimAvg
    >>> ValueSimAvg(similarity, field, float)((1,'A','1'),(-2,'B',2))
    0.5
    >>> field = lambda r: set(r[1].split(';'))
    >>> ValueSimAvg(similarity, field, float)(('A','0;1'),('B','1;2'))
    0.75
    >>> ValueSimAvg(similarity, field, float)(('A','0;1;2'),('B','0;1;2;3;4'))
    1.0
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


class ValueSimMax(ValueSim):
    """Compare the similarity of two sets of values. Set of values obtained 
    either from splitting a single column, or combining multiple columns.
    
    The similarity is the maximum of the pair-wise comparisons between the two
    sets. One perfectly matching pair of values between the two sets returns a
    similarity of 1.0.
    
    :type comparevalues: function(`V`, `V`) :class:`float`
    :param comparevalues: Compares the encoded values and returns similarity.
    :type field1: function(`R`) [`T1`,...]
    :param field1: Iterates over multi-values of the field.
    :type field2: function(`R`) [`T2`,...]
    :param field2: Iterates over multi-values of the field (default=`field1`).
    :type encode1: function(`T1`) `V`
    :param encode1: Encoder of field1 values.
    :type encode2: function(`T2`) `V`
    :param encode2: Encoder of field2 value (default=`encode1`).
    :rtype: callable(`R1`, `R2`) float
    :return: Computes maximum similarity of `R1` and `R2` over values of the field.

    >>> # define an exponential 'similarity of numbers' measure
    >>> similarity = lambda x,y: 2.0**(-abs(x-y))
    >>> field = lambda r: set([r[0],r[2]])
    >>> from dedupe.sim import ValueSimMax
    >>> ValueSimMax(similarity, field, float)((0,'A','1'),(2,'B',2))
    0.5
    >>> field = lambda r: set(r[1].split(';'))
    >>> ValueSimMax(similarity, field, float)(('A','0;1;2'),('B','3;4;5'))
    0.5
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
    
class RecordSim(_OrderedDict):
    """Returns a vector of field value similarities between two records.

    :type \*comparators: (:class:`str`, :class:`ValueSim`), ...
    :param \*comparators: Named and ordered field similarity functions.
    
    :type Weights: :class:`namedtuple` (float,...)
    :ivar Weights: type of similarity vector between records\
      with field names corresponding to the names in `comparators`.
    
    :rtype: function(`R`, `R`) :class:`W` 
    :return: Compares two records with each :class:`ValueSim` in turn,\
      returning a `W` vector [:class:`float`,...] of corresponding named\
      similarity values.

    >>> # define a 'similarity of numbers' measure
    >>> similarity = lambda x,y: 2.0**(-abs(x-y))
    >>> from dedupe.sim import ValueSim, RecordSim
    >>> vcomp1 = ValueSim(similarity, 1, float) # field 1 from record
    >>> vcomp2 = ValueSim(similarity, 2, float) # field 2 from field
    >>> rcomp = RecordSim(("V1",vcomp1),("V2",vcomp2))
    >>> rcomp(('A',1,1), ('B',2,4))
    W(V1=0.5, V2=0.125)
    """
    
    def __init__(self, *comparators):
        super(RecordSim, self).__init__(comparators)
        import dedupe.compat as c
        self.Weights = c.namedtuple("W", self.keys())

    def __call__(self, A, B):
        return self.Weights._make(
            comparator(A, B) for comparator in self.itervalues())
