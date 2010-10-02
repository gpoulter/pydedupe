"""
Compatibility layer for Python 2.x
==================================

Provides namedtuple and OrderdDict.

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
