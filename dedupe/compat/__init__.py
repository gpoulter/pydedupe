"""Compatibility module for handy classes that may only available in newer
versions of Python."""

try:
    from collections import namedtuple
except ImportError:
    from namedtuple import namedtuple
    
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
