.. PyDedupe documentation master file, created by
   sphinx-quickstart on Fri Nov 13 14:38:27 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyDedupe's documentation!
====================================

Contents:

.. toctree::
   :maxdepth: 2

   modules
   classification
   enc
   sim

To-Do List
==========

.. todolist::

Installation
============

PyDedupe is available for Python_ 2.5 or greater.

For installation from PyPi_, run `easy_install pydedupe` or using PIP
run `pip install pydedupe`.

From the extracted source run `python setup.py install`, which will
also install setuptools_ if necessary.

To install locally on linux, run::

 python setup.py install --prefix=~/.local

To check the test suite after installation, run::

 python -m dedupe.tests.__init__

.. _PyPi: http://pypi.python.org/pypi
.. _setuptools: http://pypi.python.org/pypi/setuptools
.. _Python: http://python.org/download/

How it Works
============

Deduplication takes place in three stages:

 1. Index records. For example, all records the same double-metaphone or
 soundex for the LastName field should be put in the same index block. More
 than one index can be constructed.

 2. Fox each index, compare all pairs in each index block.  For example,
 calculate the edit distance between the names, and normalised difference 
 in birthdates.  This produces a similarity vector such as (0.5, 0.2, 1.0) 
 for each pair of records.
 
 3. Classify the similarity vectors into "matches" and "non-matches". The
 similarity vector (1.0,1.0,1.0) would be a perfect match, and (0.0,0.0,0.0)
 would be a total non-match.  
 
See the page on :doc:`why we made PyDedupe <why>`

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

