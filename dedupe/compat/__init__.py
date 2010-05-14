"""
Compatibility layer for Python 2.x
==================================

Provides namedtuple and OrderdDict in case they aren't available in this version
of Python (2.5/2.6).

.. moduleauthor: Graham Poulter
"""

try:
    from collections import namedtuple
except ImportError:
    from _namedtuple import namedtuple
    
try:
    from collections import OrderedDict
except ImportError:
    from _ordereddict import OrderedDict
