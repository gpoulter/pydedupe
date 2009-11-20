PyDedupe - Record linkage tools for Python
==========================================

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

Introduction
============

Record linkage from the Encyclopedia of Public Health::

  Record linkage is the process of bringing together two or more records
  relating to the same entity(e.g., person, family, event, community,
  business, hospital, or geographical area). In 1946, H. L. Dunn of the United
  States National Bureau of Statistics introduced the term in this way: "Each
  person in the world creates a Book of Life. This Book starts with birth and
  ends with death. Record linkage is the name of the process of assembling the
  pages of this Book into a volume" (Dunn, 1946). Computerized record linkage
  was first undertaken by the Canadian geneticist Howard Newcombe and his
  associates in 1959. Newcombe recognized the full implications of extending
  the principle to the arrangement of personal files and into family
  histories. Computerized record linkage has the advantages of quality
  control, speed, consistency, reproducibility of results, and the ability to
  handle large volumes of data. For its actual implementation, Newcombe
  prepared a handbook in 1988.
  
Record linkage from `Wikipedia <http://en.wikipedia.org/wiki/Record_linkage>`::

  Record linkage (RL) refers to the task of finding entries that refer to the
  same entity in two or more files. Record linkage is an appropriate technique
  when you have to join data sets that do not have a unique database key in
  common. A data set that has undergone record linkage is said to be linked.
  
PyDedupe has been in use since January 2009 as an internal tool for linking a
directory database, where it identifies groups of records where the same
business has been entered multiple times with variations on name, address and
contact details.  This is the core library of routines.
  
Installation
============

PyDedupe runs on Python_ 2.5, 2.6 or 2.7.

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
 
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

