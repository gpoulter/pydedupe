#!/usr/bin/python

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

setup(
    name='dedupe',
    version='1.0',
    zip_safe=True,

    author='Graham Poulter',
    author_url='http://www.grahampoulter.com',
    license='GPL',
    test_suite="dedupe.tests",

    url='http://launchpad.net/pydedupe',
    description="Library for identifying similar pairs of records within or between sets for records."""
)
