#!/usr/bin/env python
import os
from jinjasql import __version__

long_description = '''
Generate SQL Queries using a Jinja2 Template.

JinjaSql automatically tracks bind parameters, and returns an array
of all parameters that can be used to execute the query.
'''

sdict = {
    'name' : 'jinjasql',
    'version' : __version__,
    'description' : 'Generate SQL Queries and Corresponding Bind Parameters using a Jinja2 Template',
    'long_description' : long_description,
    'url': 'https://github.com/hashedin/jinjasql',
    'download_url' : 'http://cloud.github.com/downloads/hashedin/jinjasql/jinjasql-%s.tar.gz' % __version__,
    'author' : 'Sripathi Krishnan',
    'author_email' : 'Sripathi@hashedin.com',
    'maintainer' : 'Sripathi Krishnan',
    'maintainer_email' : 'Sripathi@hashedin.com',
    'keywords' : ['Jinja2', 'SQL', 'Python', 'Template'],
    'license' : 'MIT',
    'packages' : ['jinjasql'],
    'test_suite' : 'tests.all_tests',
    'install_requires': [
        'Jinja2>=2.5'
    ],
    'classifiers' : [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'],
}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(**sdict)

