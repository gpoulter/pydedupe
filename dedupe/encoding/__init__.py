"""
:mod:`encoding` -- Transformation and encoding of values.
=========================================================

.. moduleauthor:: Graham Poulter
"""

import re

from _dmetaphone import dmetaphone

from functools import partial

def normspace(text):
    """Strip multiple and trailing spaces."""
    return re.sub(ur"\s+", u" ", text.strip())

def nospace(text):
    """Strip all whitespace."""
    return re.sub(ur"\s+", u"", text.strip())

def lowstrip(text):
    """Lowcase and strip extra space."""
    return normspace(text.lower())

def digits(text):
    """Strip all except digits (for phone numbers)."""
    return re.sub(ur"\D+", "", text.strip())

def sorted_words(text):
    """Sort words."""
    return ' '.join(sorted(text.split(' ')))

def reverse(text):
    """Reverse text."""
    return text[::-1]

def urldomain(text):
    """Obtain the domain from the text of a URL."""
    match = re.match(ur'(?:http://)?(?:www\.)?([^/]+)(?:/.*)?', text)
    if match is None: return text
    return match.group(1)

def emaildomain(text):
    """Obtain the domain from the text of an email address"""
    match = re.match(ur'([^@]+)@(.+)', text)
    if match is None: return text
    return match.group(2)

def wrap(*funcs):
    """Create a composited function from a list of unitary functions.
    For example, wrap(f1, f2, f3)(text) == f1(f2(f3(text)))"""
    def _wrapper(text):
        # Innermost function gets applies first
        for func in funcs[::-1]:
            text = func(text)
        return text
    return _wrapper


## Factories to create functions that can split up a single delimited 
## column or combine multiple columns. 

def multivalue(sep, *fields):
    """Return a function that combines multiple delimited fielsd as a 
    multi-value fields."""
    from dedupe.indexer import getfield
    def field_splitter(record):
        """Create a multi-value from multiple delimited fields %s using delimiter %s"""
        result = []
        for field in fields:
            value = getfield(record, field)
            values = [value] if sep is None else value.split(sep)
            result += [s.strip() for s in values if s.strip()]
        return result
    field_splitter.__doc__ %= ",".join([str(x) for x in fields]), sep
    return field_splitter

def combine(*fields):
    """Return a function that combines single-value fields as a multi-value"""
    return multivalue(None, *fields)
