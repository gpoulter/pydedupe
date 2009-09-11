#!/usr/bin/python

try:
    from distutils.core import setup
    raise ImportError()
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup

setup(
    name='dedupe',
    version='1.0',
    description="Identifies similar records within a table or between two tables.",
    author='Graham Poulter',
    author_email='http://www.grahampoulter.com',
    url='http://launchpad.net/pydedupe',
    packages='dedupe',
    zip_safe=True,
    license='GPL',
    platforms='any',
    test_suite="dedupe.tests",
)
