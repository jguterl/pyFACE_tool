#!/usr/bin/env python
# To use:
#       python setup.py install

import os, codecs
from setuptools import setup, find_packages
def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")
def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

        
version='0.0.1'
with open('pyface_tool/__version__.py','w') as ff:
    ff.write("__version__ = '%s'\n"%version)
setup(name="pyface_tool",
      version=get_version("pyface_tool/__version__.py"),
      author='R. Smirnov/J. Guterl',
      author_email="guterlj@fusion.gat.com",
      description="pyface_tool",
      packages=find_packages(include=['pyface_tool']),
     
      scripts=[],
     
      classifiers=['Programming Language :: Python :: 3']
      )
