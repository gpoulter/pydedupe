.. PyDedupe documentation master file, created by
   sphinx-quickstart on Fri Nov 13 14:38:27 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyDedupe's documentation!
====================================

Contents:

.. toctree::
   :maxdepth: 2

Installation
============

PyDedupe is available for Python_ 2.5 or greater.

For installation from PyPi_, run `easy_install pydedupe` or using PIP
run `pip install pydedupe`.

From the extracted source run `python setup.py install`, which will
also install setuptools if necessary.

To install locally on linux, run::

 python setup.py install --prefix=~/.local

To check the test suite after installation, run::

 python -m dedupe.tests.__init__

.. _PyPi: http://pypi.python.org/pypi/setuptools
.. _Python: http://python.org/download/

Module index
============

.. automodule:: dedupe.recordgroups
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

