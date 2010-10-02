"""
Getters: functions to obtain a field values from a record
=========================================================

"""

from operator import attrgetter as attr

from operator import itemgetter as item


def dictattr(fieldspec):
    def get(row):
        if isinstance(row, dict):
            return row.get(fieldspec, None)
        else:
            return getattr(row, fieldspec)
    return get


def getter(fieldspec):
    """Build a getter for unknown `fieldspec`. Returns either
    attrgetter(fieldspec) for string, itemgetter(fieldspec) for int,
    or fieldspec unchanged if it is already a function.

    >>> from collections import namedtuple
    >>> from dedupe import get
    >>> Record = namedtuple('Record', 'A B')
    >>> get.getter('A')(Record('foo','bar'))
    'foo'
    >>> get.getter(0)(('a','b','c'))
    'a'
    >>> get.getter(lambda r: r[0]+r[1])(('a','b','c'))
    'ab'
    """
    import collections
    if isinstance(fieldspec, collections.Callable):
        return fieldspec
    elif isinstance(fieldspec, int):
        return item(fieldspec)
    elif isinstance(fieldspec, str):
        return dictattr(fieldspec)
    else:
        raise TypeError("fieldspec: " + str(type(fieldspec)))


def fallback(fields, test=bool, default=""):
    """Build a getter that tries fields in order until one passes the test.

    >>> getfield = fallback((0, 2))
    >>> rec1 = ('a', 'b', 'c')
    >>> rec2 = ('', 'b', 'c')
    >>> rec3 = (None, 'b', None)
    >>> getfield(rec1)
    'a'
    >>> getfield(rec2)
    'c'
    >>> getfield(rec3)
    ''
    """
    import collections
    if not isinstance(test, collections.Callable):
        raise TypeError("test: {0!r} is not callable".format(test))
    getters = [ getter(f) for f in fields ]

    def getfield(record):
        """Attempt to get field from record"""
        for get in getters:
            try:
                val = get(record)
                if test(val):
                    return val
            except (AttributeError, KeyError):
                pass
        return default
    return getfield


def combine(*fields):
    """Build a getter that combines several fields into a list of strings.

    :param fields: List of field-getters whose values are to be combined.
    :rtype: [`V`, ...]
    :return: The virtual-field values

    >>> from dedupe import get
    >>> combiner = get.combine(0, 2, 3)
    >>> combiner(('A','B','C','D','E'))
    ['A', 'C', 'D']
    """
    return multivalue(None, *fields)


def multivalue(sep, *fields):
    """Build a getter to convert one or more separated-value fields
    into a list of strings.  For example

    :type sep: :class:`str`
    :param sep: Optional delimiter to split fields into multiple values
    :param fields: List of field-getters whose values are to be combined.
    :rtype: [`V`, ...]
    :return: The virtual-field values

    >>> from dedupe import get
    >>> rec1 = ('a;b;c',)
    >>> rec2 = ('a;b','c;d')
    >>> get.multivalue(";", 0)(rec1)
    ['a', 'b', 'c']
    >>> get.multivalue(";", 0, 1)(rec2)
    ['a', 'b', 'c', 'd']
    """
    getters = [ getter(f) for f in fields ]

    def splitcombine(record):
        """Get multi-valued from delimited fields %s using delimiter %s"""
        result = []
        for get in getters:
            value = get(record)
            values = [value] if sep is None else value.split(sep)
            result += [s.strip() for s in values if s.strip()]
        return result
    splitcombine.__doc__ %= ",".join([str(x) for x in fields]), sep
    return splitcombine
