================
 About PyDedupe
================

PyDedupe has been in use since January 2009 as an internal tool for linking a
directory database.  It identifies groups of records where the same business has
been entered multiple times with variations on name, address and contact

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

Overview of record linkage
==========================

Deduplicating a file takes place in three stages: indexing, comparison and
classification.  In the indexing stage records are put into groups, for example
by phone number or by the phonetic encoding of the last name.  In the comparison
stage, all pairs of records within a group are compared.  Each compared pair of
records gets a vector of similarities of their corresponding fields.   Each pair
is finally classified as a match or a non-match, either using rules (such as
"match when names are identical") or classification algorithms
 

