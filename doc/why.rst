.. -*- mode:rst -*-

Why not FEBRL
=============

FEBRL_ stands for Freely Extensible Biomedical Record Linkage.  It
provides functions for encoding, comparing, indexing and classifying
rows. 

Here is what PyDedupe provides over FEBRL:

- Flexible input definition. PyDedupe accepts any iteration of tuples, which
  can come from any data source. FEBRL accepts instances of its "DataSetCSV"
  class, which require naming a CSV file on the disk.

- Flexible index definition. Specify any function to take a record and return
  a tuple of index keys. FEBRL's design limits the index to string encoders
  (such as "soundex") on single fields (such as "name"). 
 
- Flexible field comparison. Specify any function to take a record and
  return a similarity value (one component of the similarity
  vector). The FEBRL classes force the use of a basic comparator (such
  as edit distance) on a single column.  PyDedupe can use multiple
  columns in a single comparison component (such as both "Phone1" and
  "Phone2", or "Latitude" and "Longitude"), and compare multi-valued
  fields such as "Tags" field holding "Books;Stores", and allows
  arbitrary transformation of the column prior to comparison.

- Flexible output formatting. FEBRL requires output to CSV files, with
  and no API to access internal data structures (they are created and
  destroyed in the space of a function), so there's no good way to
  find why some pairs matched and others did not. PyDedupe returns
  lists of record tuples and transparent data structures which can be
  processed or analysed in any manner you please.

.. _FEBRL: http://sourceforge.net/projects/febrl
