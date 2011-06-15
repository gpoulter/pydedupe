#!/usr/bin/env python
"""Library for record linkage: identifying pairs of similar records.

From `Wikipedia <http://en.wikipedia.org/wiki/Record_linkage>`::

  Record linkage (RL) refers to the task of finding entries that refer to the
  same entity in two or more files. Record linkage is an appropriate technique
  when you have to join data sets that do not have a unique database key in
  common. A data set that has undergone record linkage is said to be linked.
"""

try:
    from setuptools import setup
except ImportError:
    try:
        from distribute_setup import use_setuptools
        use_setuptools()
        from setuptools import setup
    except ImportError:
        from distutils.core import setup

extra = {}
import sys
if sys.version_info >= (3,):
    extra['use_2to3'] = True
    extra['convert_2to3_doctests'] = ['doc/tutorial.rst']

extra['classifiers'] = [c.strip() for c in """
Development Status :: 4 - Beta
Intended Audience :: Developers
Intended Audience :: Information Technology
License :: OSI Approved :: GNU General Public License (GPL)
Topic :: Text Processing :: Linguistic
Topic :: Scientific/Engineering :: Information Analysis
Topic :: Scientific/Engineering :: Artificial Intelligence
Environment :: Console
Operating System :: OS Independent
Programming Language :: Python :: 2
Programming Language :: Python :: 2.6
""".split('\n') if c.strip()]

doclines = __doc__.split("\n")
extra['description'] = doclines[0]
extra['long_description'] = "\n".join(doclines[2:])

setup(
    name='pydedupe',
    version='1.0',
    packages=['dedupe', 'dedupe.compat', 'dedupe.classification'],
    author='Graham Poulter',
    maintainer='Graham Poulter',
    license='http://www.fsf.org/licensing/licenses/gpl.html',
    url='http://launchpad.net/pydedupe',
    download_url='http://pypi.python.org/pypi/pydedupe',
    keywords='record linkage, deduplication, entity resolution',
    test_suite='tests',
    zip_safe=True,
    platforms='any',
    **extra
)
