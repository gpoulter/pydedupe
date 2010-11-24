"""
Compare values, fields, and records for similarity
==================================================

.. moduleauthor:: Graham Poulter
"""

import collections
import logging

from dedupe.dale import similarity as dale
from dedupe.levenshtein import similarity as levenshtein
from dedupe.compat import OrderedDict as _OrderedDict

LOG = logging.getLogger(__name__)


class Convert(object):
    """Gets a single-valued field and converts it to a comparable value.

    :type field: `callable` or `str` or `int`
    :param field: Specifies a field from the record record.
    :type converter: `callable`
    :param converter: Converts field value for comparison.
    :return: Converted field value.

    >>> c = Convert(1, lambda x:x.lower())
    >>> rec = ('A','B','C')
    >>> c(rec)
    'b'
    """

    def __init__(self, field, converter):
        from dedupe.get import getter
        self.field = field
        self.getter = getter(field)
        self.converter = converter

    def __call__(self, record):
        return self.converter(self.getter(record))


class ListConvert(Convert):
    """Gets a multi-valued field converts its values to comparable values.

    :type field: `callable`
    :param field: Specifies a field from the record record.
    :type converter: `callable`
    :param converter: Converts field value for comparison.
    :return: List of converted field values.

    >>> c = ListConvert(lambda x:x[1].split(';'), lambda x:x.lower())
    >>> rec = ('A','X;Y;Z','C')
    >>> c(rec)
    ['x', 'y', 'z']
    """

    def __call__(self, record):
        return [self.converter(v) for v in self.getter(record)]


class Scale(object):
    """Map values of a similarity function onto the 0.0 to `rmax` range.

    :param similarity: Callable of two records returning a similarity value.
    :param low: Similarity values below `low` (default 0.0) are scaled to 0.0
    :param high: Similarity values above `high` (default 1.0) are scaled to 1.0
    :param rmax: Upper end of the result range (default 1.0).\
    Lower `rmax` reduces contribution to vector distance, downweighting it.
    :param missing: Return `missing` when `similarity` returns `None`.
    :param test: Callable of record to test bad values.  If `a` and `b` pass\
    the test then return `similarity(a, b)`, otherwise return `missing`.

    >>> from dedupe import sim
    >>> simfunc = lambda a, b: 2**-abs(a-b)
    >>> simfunc(1, 2)
    0.5
    >>> sim.Scale(simfunc)(1, 2)
    0.5
    >>> sim.Scale(simfunc, low=0.6)(1, 2)
    0.0
    >>> sim.Scale(simfunc, high=0.4)(1, 2)
    1.0
    >>> sim.Scale(simfunc, low=0.4, high=0.6)(1, 2)
    0.5
    >>> sim.Scale(simfunc, low=0.4, high=0.6, rmax=0.5)(1, 2)
    0.25
    >>> isnum = lambda x: isinstance(x, int) or isinstance(x, float)
    >>> print sim.Scale(simfunc, test=isnum)("blah", 2)
    None
    """

    def __init__(self, similarity,
                 low=0.0, high=1.0, rmax=1.0, missing=None, test=None):
        if not (0.0 <= low < high):
            raise ValueError("low: {0}, high: {1}".format(low, high))
        self.similarity = similarity
        self.low = low
        self.high = high
        self.rmax = rmax
        self.missing = missing
        self.test = test

    def scale(self, value):
        """Scale a value from (low, high) range to (0, 1) range."""
        if value <= self.low:
            return 0.0
        if  value >= self.high:
            return 1.0
        return self.rmax * (value - self.low) / (self.high - self.low)

    def __call__(self, a, b):
        """Similarity of a and b, scaled to (0, 1) range."""
        if self.test and not (self.test(a) and self.test(b)):
            return self.missing
        v = self.similarity(a, b)
        if v is None:
            return self.missing
        return self.scale(v)


class Field(object):
    """Computes the similarity of a pair of records on a specific field.

    :type compare: callable(`V`, `V`) :class:`float`
    :param compare: Returns similarity of a pair of encoded field values.

    :type field1: callable(`R`) -> `T1`
    :param field1: Gets field value from first record.
    :type encode1: callable(`T1`) `V`
    :param encode1: Encodes field value from first record (`lambda x:x`)

    :type field2: callable(`R`) -> `T1`
    :param field2: Gets field value from the second record (`field1`)
    :type encode2: callable(`T1`) `V`
    :param encode2: Encodes field value from the second record (`encode1`)

    >>> # define some 'similarity of numbers' measure
    >>> similarity = lambda x, y: 2**-abs(x-y)
    >>> similarity(1, 2)
    0.5
    >>> Field(similarity, lambda r:r[1], float)(('A', '1'), ('B', '2'))
    0.5
    >>> fsim = Field(similarity, field1=lambda r:r[0], encode1=lambda x:x,
    ...              field2=lambda r:r[1], encode2=float)
    >>> fsim((1, 'A'), ('B', '2'))
    0.5
    """

    def __init__(
        self, compare, field1, encode1=None, field2=None, encode2=None):
        from dedupe.get import getter
        self.compare = compare
        self.field1 = getter(field1)
        self.encode1 = encode1 if encode1 else lambda x: x
        self.field2 = getter(field2) if field2 else self.field1
        self.encode2 = encode2 if encode2 else self.encode1

    def __call__(self, record1, record2):
        """Returns the similarity of `record1` and `record2` on this field."""
        v1 = self.field1(record1)
        v2 = self.field2(record2)
        if v1 is not None and v2 is not None:
            return self.compare(self.encode1(v1), self.encode2(v2))
        else:
            return None


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
    :type field1: callable(`R`) [`T1`, ...]
    :param field1: Returns a list of values for the field on first record.
    :type field2: callable(`R`) [`T2`, ...]
    :param field2: Returns a list of values for the field on second record \
    (default: `field1`).
    :type encode1: function(`T1`) `V`
    :param encode1: Encodes each field1 value for comparison.
    :type encode2: function(`T2`) `V`
    :param encode2: Encodes each field2 value for comparison (`encode1`).

    :rtype: callable(`R1`, `R2`) float
    :return: Computer of average similarity of records `R1` and `R2`\
    for values of the field.

    >>> # define an exponential 'similarity of numbers' measure
    >>> similarity = lambda x, y: 2.0**(-abs(x-y))
    >>> field = lambda r: set([r[0], r[2]])
    >>> from dedupe import sim
    >>> sim.Average(similarity, field, float)((1, 'A', '1'), (-2, 'B', 2))
    0.5
    >>> field = lambda r: set(r[1].split(';'))
    >>> sim.Average(similarity, field, float)(('A', '0;1'), ('B', '1;2'))
    0.75
    >>> sim.Average(similarity, field, float)(
    ...             ('A', '0;1;2'), ('B', '0;1;2;3;4'))
    1.0
    """

    def __call__(self, record1, record2):
        """Return the average similarity of `record1` and `record2` on
        this multi-valued field"""
        f1 = set(self.encode1(v1) for v1 in self.field1(record1))
        f2 = set(self.encode2(v2) for v2 in self.field2(record2))
        f1, f2 = sorted([f1, f2], key=len)  # short set, long set
        # Missing value check
        if len(f1) == 0 or len(f2) == 0:
            return self.compare(None, None)
        total = 0.0
        for v1 in f1:
            best = 0.0
            for v2 in f2:
                comp = self.compare(v1, v2)
                best = max(best, comp)
            total += best  # score of most similar item in the long set
        return total / len(f1)


class Maximum(Field):
    """Computes the maximum similarity of a pair of records on a
    multi-valued field.

    :type compare: callable(`V`, `V`) :class:`float`
    :param compare: Returns similarity of a pair of encoded field values.
    :type field1: callable(`R`) [`T1`, ...]
    :param field1: Returns a list of values for the field on first record.
    :type field2: callable(`R`) [`T2`, ...]
    :param field2: Returns a list of values for the field on second record\
    (default: `field1`).
    :type encode1: function(`T1`) `V`
    :param encode1: Encodes each field1 value for comparison.
    :type encode2: function(`T2`) `V`
    :param encode2: Encodes each field2 value for comparison\
    (default: `encode1`).

    >>> # define an exponential 'similarity of numbers' measure
    >>> similarity = lambda x, y: 2.0**(-abs(x-y))
    >>> field = lambda r: set([r[0], r[2]])
    >>> from dedupe import sim
    >>> sim.Maximum(similarity, field, float)((0, 'A', '1'), (2, 'B', 2))
    0.5
    >>> field = lambda r: set(r[1].split(';'))
    >>> sim.Maximum(similarity, field, float)(('A', '0;1;2'), ('B', '3;4;5'))
    0.5
    """

    def __call__(self, record1, record2):
        """Return the maximum similarity of `record1` and `record2` on
        this multi-valued field."""
        f1 = set(self.encode1(v1) for v1 in self.field1(record1))
        f2 = set(self.encode2(v2) for v2 in self.field2(record2))
        # Missing value check
        if len(f1) == 0 or len(f2) == 0:
            return self.compare(None, None)
        best = 0.0
        for v1 in f1:
            for v2 in f2:
                comp = self.compare(v1, v2)
                best = max(best, comp)
        return best


class Record(_OrderedDict):
    """Returns a vector of field value similarities between two records.

    :type \*simfuncs: [(:class:`str`, :class:`Field`), ...]
    :param \*simfuncs: Pairs of (field name, similarity function) used\
    to compute the tuple of similarities.

    :ivar Similarity: namedtuple class for the similarity of a pair of records\
    with field names corresponding to `simfuncs`.

    :rtype: function(`R`, `R`) :class:`Similarity`
    :return: Takes two records and returns a `Similarity` tuple.

    >>> # define a 'similarity of numbers' measure
    >>> similarity = lambda x, y: 2.0**(-abs(x-y))
    >>> from dedupe import sim
    >>> vcomp1 = sim.Field(similarity, 1, float) # field 1 from record
    >>> vcomp2 = sim.Field(similarity, 2, float) # field 2 from field
    >>> rcomp = sim.Record(("V1", vcomp1), ("V2", vcomp2))
    >>> rcomp(('A', 1, 1), ('B', 2, 4))
    Similarity(V1=0.5, V2=0.125)
    """

    def __init__(self, *simfuncs):
        super(Record, self).__init__(simfuncs)
        self.Similarity = collections.namedtuple("Similarity", self.keys())

    def __call__(self, A, B):
        return self.Similarity._make(
            simfunc(A, B) for simfunc in self.itervalues())


class Indices(_OrderedDict):
    """Dictionary containing indeces defined on a single set of records.
    When comparing, it caches the similarity vectors so that a pair of records
    compared in one index is not compared again if the pair shows up in one
    of the other indeces.

    :type strategy: [ (`str`, `type`, `function`), ... ]
    :param strategy: List of indexing strategies, as\
    (index name, index class, key function). The index class must support\
    the `compare` method, and the key function takes a record and returns\
    a list of keys for indexing.

    :type records: [ `tuple`, ... ]
    :param records: List of records to insert into the indeces.

    >>> from dedupe import block, sim
    >>> makekey = lambda r: [int(r[1])]
    >>> makekey(('A', 3.5))
    [3]
    >>> strategy = [ ("MyIndex", block.Index, makekey) ]
    >>> records1 = [('A', 5.5), ('B', 4.5), ('C', 5.25)]
    >>> records2 = [('D', 5.5), ('E', 4.5), ('F', 5.25)]
    >>> sim.Indices(strategy, records1)
    OrderedDict([('MyIndex', {4: [('B', 4.5)], 5: [('A', 5.5), ('C', 5.25)]})])
    >>> sim.Indices.check_strategy((1, 2, 3))
    Traceback (most recent call last):
        ...
    TypeError: 1: not a string.
    >>> sim.Indices.check_strategy([])
    Traceback (most recent call last):
        ...
    TypeError: []: not a strategy triple.
    """

    def __init__(self, strategy, records=[]):
        for strat in strategy:
            self.check_strategy(strat)
        super(Indices, self).__init__(
            (name, idxtype(keyfunc, records))
            for name, idxtype, keyfunc in strategy)

    @staticmethod
    def check_strategy(strategy):
        """Raise TypeError if strategy tuple is wrong in some way."""
        if len(strategy) != 3:
            raise TypeError("{0!r}: not a strategy triple.".format(strategy))
        name, idxtype, keyfunc = strategy
        if not isinstance(name, basestring):
            raise TypeError("{0!r}: not a string.".format(name))
        if not hasattr(idxtype, "compare") and hasattr(idxtype, "insert"):
            raise TypeError("{0!r}: not an index type.".format(idxtype))
        if not callable(keyfunc):
            raise TypeError("{0!r}: not callable.".format(keyfunc))

    def insert(self, record):
        """Insert a record into each :class:`Index`."""
        for index in self.itervalues():
            index.insert(record)

    def compare(self, simfunc, other=None):
        """Compute similarities of indexed pairs of records.

        :type simfunc: func(`R`, `R`) (`float`, ...)
        :param simfunc: takes pair of records and returns a similarity vector.

        :type other: :class:`Indices`
        :param other: Another Indices to compare against.

        :rtype: {(R, R):(float, ...)}
        :return: mapping from pairs of records similarity vectors.
        """
        comparisons = {}
        if other is None or other is self:
            for index in self.itervalues():
                index.compare(simfunc, None, comparisons)
        else:
            for index1, index2 in zip(self.itervalues(), other.itervalues()):
                if type(index1) is not type(index2):
                    raise TypeError(
                        "Indeces of type {0} and type {1} are incompatible"\
                        .format(type(index1), type(index2)))
                index1.compare(simfunc, index2, comparisons)
        return comparisons

    def log_comparisons(self, other):
        """Log the expected between-index comparisons."""
        if other is not None and other is not self:
            for (n1, i1), (n2, i2) in zip(self.items(), other.items()):
                LOG.info("name=TwoIndexCompare idx1=%s idx2=%s comparisons=%s",
                         n1, n2, i1.count(i2))
                i1.log_size(n1)
                i2.log_size(n2)
        else:
            for name, index in self.iteritems():
                LOG.info("name=OneIndexCompare idx=%s comparisons=%s",
                         name, index.count())
                index.log_size(name)
