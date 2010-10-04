"""
Compatibility layer for Python 2.x
==================================

Provides namedtuple and OrderdDict.

.. moduleauthor: Graham Poulter
"""

try:
    from collections import namedtuple
except ImportError:
    from dedupe.compat._namedtuple import namedtuple

try:
    from collections import OrderedDict  # pylint: disable=E0611
except ImportError:
    from dedupe.compat._ordereddict import OrderedDict
