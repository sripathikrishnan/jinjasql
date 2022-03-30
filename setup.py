#!/usr/bin/env python
import os

# Duplicating version from jinjasql.__init__.py
# We can't directly import it from jinjasql,
# because during installation Jinja2 isn't installed as yet
# 
# There are several approaches to eliminate this redundancy,
# see https://packaging.python.org/single_source_version/
# but for now, we will simply maintain it in two places
__version__ = '0.1.8'

long_description = '''
Generate SQL Queries using a Jinja Template, without worrying about SQL Injection

JinjaSQL automatically binds parameters that are inserted into the template.
After JinjaSQL evaluates the template, you get 1) Query with placeholders
for parameters, and 2) List of values that need to be bound to the query. 

JinjaSQL doesn't actually execute the query - it only prepares the 
query and the bind parameters. You can execute the query using any 
database engine / driver you are working with.

'''

sdict = {
    'name' : 'jinjasql',
    'version' : __version__,
    'description' : 'Generate SQL Queries and Corresponding Bind Parameters using a Jinja2 Template',
    'long_description' : long_description,
    'url': 'https://github.com/sripathikrishnan/jinjasql',
    'download_url' : 'http://cloud.github.com/downloads/sripathikrishnan/jinjasql/jinjasql-%s.tar.gz' % __version__,
    'author' : 'Sripathi Krishnan',
    'author_email' : 'Sripathi.Krishnan@gmail.com',
    'maintainer' : 'Sripathi Krishnan',
    'maintainer_email' : 'Sripathi.Krishnan@gmail.com',
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
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(**sdict)

