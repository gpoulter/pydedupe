.. -*- mode:rst -*-

===============================
 PyDedupe - Duplicate Detector
===============================

PyDedupe links similar pairs of records within a list of records,
or between two lists of records.  The output consists of 
pairs of records that PyDedupe considers to be very similar.  

Where those records came from (CSV, database) and what you do with the
similar pairs (delete one, merge both) is left as an exercise.

PyDedupe finds those similar pairs of records in three steps:

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
 
There is a convenience function that takes your index definition, 
comparator definition, classifier definition and list(s) of records, 
and returns the most similar pairs.  You can also define your own process
from the pieces.  

If you have a large number of records, unsupervised clustering is able to
classify the compared pairs of record as matches or non-matches. Otherwise you
will need supervised classification to get satisfactory results, where you
give it some examples of matches and non-matches for it to learn from. Provide
the training data as a set of records plus a list of pairs of records which
have been manually identified as matches.


FEBRL: Freely Extensible Biomedical Record Linkage
==================================================

The _FEBRL project provides a wide selection of encoding, comparison and
classification methods. Although it implements many methods, the FEBRL class
hierarchy places artificial restrictions on what data it acceps (CSV files
only) and on what sorts of indexing and comparison schemes can be defined.

PyDedupe provides the ultimate flexibility in defining the index and
comparison critera, while including the FEBRL modules that providing the basic
text encoders (for indexing) and basic string comparators (for record
comparison):

The following three FEBRL modules are included in this package:

- `febrl.classification`: Classifiers of similarity vectors, such as KMeans and SVM
- `febrl.comparison`: String comparison objects, such as edit distance
- `febrl.encode`: String encoding functions, such as Double Metaphone

Unique Features in PyDedupe
===========================

- Flexible input definition. PyDedupe accepts any iteration of tuples, which
can come from any data source. FEBRL accepts instances of its "DataSetCSV"
class, which require naming a CSV file on the disk.

- Flexible index definition. Specify any function to take a record and return
a tuple of index keys. FEBRL's design limits the index to string encoders
(such as "soundex") on single fields (such as "name"). 
 
- Flexible field comparison. Specify any function to take a record and return
a similarity value (one component of the similarity vector). The FEBRL classes
force the use of a basic comparator (such as edit distance) on a single column.
PyDedupe can use multiple columns in a single comparison component (such as both
"Phone1" and "Phone2", or "Latitude" and "Longitude"), and compare
multi-valued fields such as "Tags" field holding "Books;Stores", and allows
arbitrary transformation of the column prior to comparison.

- Flexible output formatting. FEBRL requires output to CSV files in a particular
defined formats, while PyDedupe returns simple Python dicts and lists of
record tuples.

In summary, PyDedupe provides a library for defining arbitrary record linkage
criteria, making it able to solve a wider class of linkage problems.

__ FEBRL_ http://sourceforge.net/projects/febrl
