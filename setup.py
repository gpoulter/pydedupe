#!/usr/bin/python

try:
    from setuptools import setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup

setup(
    name='dedupe',
    version='1.0',
    description="""Identifies similar tuples in a list or between two lists.
    Has modules to handle CSV input and output..""",
    author='Graham Poulter',
    author_email='http://www.grahampoulter.com',
    url='http://launchpad.net/pydedupe',
    packages=['dedupe'],
    zip_safe=True,
    license='GPL',
    platforms='any',
    test_suite="dedupe.tests",
)
