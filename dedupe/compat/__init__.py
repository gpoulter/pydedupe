"""
Compatibility for Python 2.6
============================

Provides OrderdDict.

.. moduleauthor: Graham Poulter
"""

try:
    from collections import OrderedDict  # pylint: disable=E0611
except ImportError:
    from dedupe.compat._ordereddict import OrderedDict
