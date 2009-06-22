"""Field value encoding functions. 

Be careful to combine encoders in a compatible type sequence. If one encoder
produces a floating point value, don't wrap it in one that expects a string.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
"""

import re

from functools import partial

from dmetaphone import dmetaphone

from indexer import getfield

def identity(x):
    """Identity function, returns its argument."""
    return x

def strip(text):
    """Strip multiple and trailing spaces."""
    return re.sub(r"\s+", " ", text.strip())

def lowstrip(text):
    """Lowcase and strip extra space."""
    return strip(text.lower())

def nospace(text):
    """Strip all whitespace."""
    return re.sub(r"\s+", "", text.strip())

def digits(text):
    """Strip all except digits (for phone numbers)."""
    return re.sub(r"\D+", "", text.strip())

def sorted_words(text):
    """Sort words."""
    return ' '.join(sorted(text.split(' ')))

def reverse(text):
    """Reverse text."""
    return text[::-1]

def urldomain(text):
    """Obtain the domain from the text of a URL."""
    match = re.match(r'(?:http://)?(?:www\.)?([^/]+)(?:/.*)?', text)
    if match is None: return text
    return match.group(1)

def emaildomain(text):
    """Obtain the domain from the text of an email address"""
    match = re.match(r'([^@]+)@(.+)', text)
    if match is None: return text
    return match.group(2)

def wrap(*funcs):
    """Create a composited function from a list of unitary functions.
    @note: wrap(f1, f2, f3)(text) == f1(f2(f3(text)))"""
    def _wrapper(text):
        # Innermost function gets applies first
        for func in funcs[::-1]:
            text = func(text)
        return text
    return _wrapper


## Function factories for creating computed fields that contain a set of values
## instead of a single value.  The factories generate functions that can
## that split up a single delimited column or combines multiple columns.

def combined_fields(fields):
    """Creates a function that computes a set-type field from several string columns."""
    def set_of_fields(record):
        """Construct a set-type field from columns %s."""
        return [getfield(record, field).strip() for field in fields if getfield(record, field).strip()]
    set_of_fields.__doc__ %= ", ".join(fields) # Document the function
    return set_of_fields

def split_field(field, sep=";"):
    """Create a function to compute a set-type field from a delimited string column."""
    def set_from_field(record):
        """Create a set-type field from column %s using delimiter %s."""
        return [s.strip() for s in getfield(record, field).split(sep) if s.strip()]
    set_from_field.__doc__ %= (field, sep) # Document the function
    return set_from_field
