"""
Block index that groups records sharing a key
=============================================

The Index is a dictionary from key to a set of records.  When a record
similarity function is applied, it only compares pairs of records that
have same index key, which saves a lot of comparisons.

For example, indexing on the double-metaphone of a field will mean only
computing similarity vectors for pairs records that have the same
douple-metaphone.

.. moduleauthor:: Graham Poulter
"""

import logging

LOG = logging.getLogger(__name__)


class Index(dict):
    """Mapping from index key to records.

    :type makekey: function(`R`) [`K`, ...]
    :param makekey: Generates the index keys for the record.

    :type records: [`R`, ...]
    :param records: Initial records to load into the index.

    >>> makekey = lambda r: [int(r[1])]
    >>> makekey(('A', 3.5))
    [3]
    >>> compare = lambda x, y: 2**-abs(float(x[1])-float(y[1]))
    >>> compare(('A', '5.5'), ('B', '4.5'))
    0.5
    >>> from dedupe import block
    >>> a = block.Index(makekey, [('A', 5.5), ('B', 4.5), ('C', 5.0)])
    >>> a.count()
    1
    >>> a.compare(compare)
    {(('A', 5.5), ('C', 5.0)): 0.70710678118654757}
    >>> b = block.Index(makekey, [('D', 5.5), ('E', 4.5)])
    >>> a.count(b)
    3
    >>> a.compare(compare, b)
    {(('C', 5.0), ('D', 5.5)): 0.70710678118654757,\
    (('A', 5.5), ('D', 5.5)): 1.0, (('B', 4.5), ('E', 4.5)): 1.0}
    """

    def __init__(self, makekey, records=None):
        super(Index, self).__init__()
        self.makekey = makekey
        if records:
            for record in records:
                self.insert(record)

    def insert(self, record):
        """Insert a record into the index.

        :type record: :class:`namedtuple` or other record.
        :param record: The record object to index.
        :rtype: [`K`, ...]
        :return: Keys under which the record was inserted.
        """
        keys = self.makekey(record)
        for key in keys:
            if key is None or key == "":
                raise ValueError("Empty index key in %s for record %s" % (
                    repr(keys), repr(record)))
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
                    comparisons += len(recs) * (len(recs) - 1) // 2
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

        :type compare: function(`R1`, `R2`) [`float`, ...]
        :param compare: Function for comparing a pair of records.

        :type other: :class:`Index`
        :param other: Optional second index to compare against.

        :type comparisons: {(`R1`, `R2`):[`float`, ...]}
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
        """Perform within-index comparisons."""
        if comparisons is None:
            comparisons = {}
        for records in self.itervalues():
            records.sort()  # sort the group to ensure a < b
            for j in range(len(records)):
                for i in range(j):
                    # i < j, and sorting means record[i] <= record[j]
                    a, b = records[i], records[j]
                    # same record indexed under multiple keys!
                    if a is b:
                        continue
                    # now compare a and b, keeping a <= b
                    if (a, b) not in comparisons:
                        comparisons[(a, b)] = compare(a, b)
        return comparisons

    def _compare_other(self, compare, other, comparisons=None):
        """Perform comparisons against another index."""
        if comparisons is None:
            comparisons = {}
        for indexkey in self.iterkeys():
            if indexkey in other.iterkeys():
                for rec1 in self[indexkey]:
                    for rec2 in other[indexkey]:
                        pair = (rec1, rec2)
                        if pair not in comparisons:
                            comparisons[pair] = compare(pair[0], pair[1])
        return comparisons

    def log_size(self, name):
        """Log statistics about block sizes for `index`, prefixing with `name`.

        >>> from dedupe import block
        >>> makekey = lambda r: [int(r[1])]
        >>> idx = block.Index(makekey, [('A', 5.5), ('B', 4.5), ('C', 5.25)])
        >>> def log(s, *a):
        ...     print s % a
        >>> LOG.info = log
        >>> idx.log_size("NumIdx")
        name=IdxSize idx=NumIdx recs=3 blocks=2 max=2 avg=1.50
        """
        if self:
            records = sum(len(recs) for recs in self.itervalues())
            largest = max(len(recs) for recs in self.itervalues())
            blocks = len(self)
            LOG.info("name=IdxSize idx=%s recs=%s blocks=%s max=%s avg=%.2f",
                     name, records, blocks, largest, float(records) / blocks)
        else:
            LOG.info("name=EmptyIndex idx=%s",  name)
