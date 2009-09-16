"""Field value encoding functions. 

Be careful to combine encoders in a compatible type sequence. If one encoder
produces a floating point value, don't wrap it in one that expects a string.

@author: Graham Poulter
@copyright: MIH Holdings
@license: GPL
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
    @note: wrap(f1, f2, f3)(text) == f1(f2(f3(text)))"""
    def _wrapper(text):
        # Innermost function gets applies first
        for func in funcs[::-1]:
            text = func(text)
        return text
    return _wrapper


## Factories to create functions that can split up a single delimited 
## column or combine multiple columns. 

from dedupe.indexer import getfield

def combine_fields(*fields):
    """Creates a function that computes a multi-valued field from multiple columns."""
    def field_combiner(record):
        """Construct a multi-valued field from columns %s."""
        return [getfield(record, field).strip() for field in fields if getfield(record, field).strip()]
    field_combiner.__doc__ %= ", ".join([str(x) for x in fields]) # Document the function
    return field_combiner

def split_field(field, sep=";"):
    """Create a function to compute a multi-valued field from a delimited column."""
    def field_splitter(record):
        """Create a set-type field from column %s using delimiter %s."""
        return [s.strip() for s in getfield(record, field).split(sep) if s.strip()]
    field_splitter.__doc__ %= (field, sep) # Document the function
    return field_splitter
