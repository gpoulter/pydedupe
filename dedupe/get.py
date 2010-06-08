"""
Getters: functions to obtain a field values from a record
=========================================================

"""

from operator import attrgetter as attr

from operator import itemgetter as item

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
    if callable(fieldspec):
        return fieldspec
    elif isinstance(fieldspec, str):
        return attr(fieldspec)
    elif isinstance(fieldspec, int):
        return item(fieldspec)
    else:
        raise TypeError("fieldspec: " + str(type(fieldspec)))

def getany(record, field):
    """Get field from a record by any of attribute lookup (string), index
    lookup (int), or application (function).

    :type record: :class:`namedtuple` or :class:`tuple`
    :param record: record from which to retriev the field value
    :type field: :class:`str`, :class:`int`, or function(`R`)
    :param field: Attempt to return R.field, R[field] or field(R)
    :return: Value of `field` in `record`

    >>> from collections import namedtuple
    >>> from dedupe import get
    >>> Record = namedtuple('Record','A B')
    >>> get.getany(Record('foo','bar'), 'A')
    'foo'
    >>> get.getany(('a','b'), 0)
    'a'
    >>> get.getany(('a','b'), lambda r: r[0]+r[1])
    'ab'
    """
    if callable(field):
        return field(record)
    elif isinstance(field, str):
        return getattr(record, field)
    elif isinstance(field, int):
        return record[field]
    else:
        raise TypeError("field: " + str(type(fieldspec)))

def fallback(fields, test=bool, default=None):
    """Build a getter that tries fields in order until one passes the test."""
    def getfield(record):
        """Attempt to get field from record"""
        for field in fields:
            try:
                val = getany(row, field)
                if test(val):
                    return val
            except AttributeError:
                pass
            else:
                break
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
    >>> get.multivalue(";", 0)(('a;b;c',))
    ['a', 'b', 'c']
    >>> get.multivalue(";", 0, 1)(('a;b','c;d'))
    ['a', 'b', 'c', 'd']
    """
    def splitcombine(record):
        """Get multi-valued from delimited fields %s using delimiter %s"""
        result = []
        for field in fields:
            value = getany(record, field)
            values = [value] if sep is None else value.split(sep)
            result += [s.strip() for s in values if s.strip()]
        return result
    splitcombine.__doc__ %= ",".join([str(x) for x in fields]), sep
    return splitcombine

