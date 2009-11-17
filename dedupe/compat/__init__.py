"""
:mod:`compat` -- Python 2.6 features
=====================================

.. module:: compat
   :synopsis: Provide classes only available in newer versions of Python.
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

from _bunch import bunch
