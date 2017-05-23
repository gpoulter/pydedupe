# Python deduplication library

PyDedupe is a Python library for performing record linkage, identifying similar groups of records. 

I wrote it while working at Naspers, and received permissino to publish it under the GNU General Public License.   

PyDedupe was written to remove the limitations of then-existing record linkage tools by supporting a general model of tabular data and decoupling the input formats from the algorithm. FEBRL, the only other Python record linkage library supported only scalar-valued fields. PyDedupe supports row transformations for generated fields, multi-valued fields derived from delimited values in a column or combined from several columns, and compound values (such as geographic coordinates).  The API is operates on iterations of tuples so that it is decoupled from input formats (such as a database or delimited text file).   A convenience module is provided for loading records from CSV files and re-writing them with similar records grouped together.

The general strategy for record linkage is:

1. Index records into blocks
2. Compare all pairs of records in each block with a similarity function
3. Cluster record pairs into "matches" and "non-matches" from the vector of similarity values.

The PyDedupe API can be used at multiple levels of abstraction:

* Low-level functions to
  * Normalise values
  * Generate indexed values
  * Compare values for similarity
  * Do binary classification of floating-point vectors
* Higher level classes to
  * Index records into blocks
  * Compare pairs of records for similarity vectors
  * Classify pairs of records as matches/non-matches
  * Group records together
* Highest level API to
  * Use a record linkage strategy
  * Accept records from CSV input and write groups to CSV output

Using the library on CSV files requires writing a small script that defines the strategies for indexing, comparison and classification, then calls a high-level function with the name of the CSV input file and a folder in which to write the output. Records may be linked either within a single file, or between two files.

Record linkage on a database requires writing additional code to retrieves tuples, using the PyDedupe API to index, compare and classify the tuples, thentag the pairs of linked records in the database - or present a user interface for manually merging them.
