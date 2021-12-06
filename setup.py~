#!/usr/bin/env python
# To use:
#       python setup.py install
#
import sys
import numpy
import os
import codecs
import os.path
import string
import site
from Forthon.compilers import FCompiler
import getopt
from setuptools import setup, distutils, find_packages
from distutils.core import Extension, Distribution
#from distutils.command.build_py import build_py as _build_py
from setuptools.command.build_ext import build_ext

import subprocess


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")
GitHash=''
GitRemoteRepo=''
GitBranch=''
GitTag=''
GitRepo=''
try:
    import git #gitpython
    Repo=git.Repo()
    GitHash=Repo.head.object.hexsha
    GitBranch=Repo.active_branch.name
    #GitRepo=Repo.active_branch.repo.name
except:
    pass




# optlist, args = getopt.getopt(sys.argv[1:], 'gt:F:', ['parallel', 'petsc','omp','nersc'])
machine = sys.platform
debug = 0
fcomp = None
parallel = 0
petsc = 0
OMP=False
# for o in optlist:
#     if o[0] == '-g':
#         debug = 1
#     elif o[0] == '-t':
#         machine = o[1]
#     elif o[0] == '-F':
#         fcomp = o[1]
#     elif o[0] == '--parallel':
#         parallel = 1
#     elif o[0] == '--petsc':
#         petsc = 1
#     elif o[0] == '--omp':
#         OMP = True
#     elif o[0] == '--fcomp':
#         fcomp=o[1]

# OMP add-on
#OMPpackages=['bbb','com','api']
#OMPlisthtreadprivatevars='../../ppp/ListVariableThreadPrivate_final.txt'
CARGS=[]
FARGS=['-g -fmax-errors=15', '-DFORTHON','-cpp','-Wconversion','-fimplicit-none']
# if OMP:
#     FARGS=FARGS+['-fopenmp']
#     CARGS=CARGS+['-fopenmp']
#     OMPargs=['--omp']
# else:
OMPargs=[]
OMPFLAGS='OMPFLAGS = {}'.format(' '.join(OMPargs))

# # Flags for makefile. Flags are easier to handle from setup.py and it prevents dealing with the makefile.)

# FARGSDEBUG=['-fbacktrace','-ffree-line-length-0', '-fcheck=all','-ffpe-trap=invalid,overflow,underflow -finit-real=snan','-Og']
# FARGSOPT=['-Ofast']

# if debug==1:
#     FARGS=FARGS+FARGSDEBUG
# else:
#     FARGS=FARGS+FARGSOPT

FLAGS ='DEBUG = -v --fargs "{}"'.format(' '.join(FARGS))
if CARGS!=[]:
    FLAGS =FLAGS+' --cargs="{}"'.format(' '.join(CARGS))



#sys.argv = ['setup2.py']+args
fcompiler = FCompiler(machine=machine,
                      debug=debug,
                      fcompname=fcomp)


class face_build(build_ext):
    def run(self):

        subprocess.call(['make',FLAGS,OMPFLAGS, '-f', 'Makefile.Forthon3'])
        build_ext.run(self)


class face_clean(build_ext):
    def run(self):
        subprocess.call(['make', '-f', 'Makefile.Forthon3', 'clean'])
        #clean.run(self)

#facepkgs = ['face']


# def makeobjects(pkg):
#     return [pkg+'_p.o', pkg+'pymodule.o']


uedgeobjects = []

# add here any extra dot o files other than pkg.o, pkg_p.o


dummydist = Distribution()
dummydist.parse_command_line()
dummybuild = dummydist.get_command_obj('build')
dummybuild.finalize_options()
builddir = dummybuild.build_temp

uedgeobjects = map(lambda p: os.path.join(builddir, p), uedgeobjects)

library_dirs = fcompiler.libdirs
libraries = fcompiler.libs




with open('pyface/__git__.py','w') as ff:
    #ff.write("__version__ = '%s'\n"%version)
    ff.write("tag='{}'\n".format(GitTag))
    ff.write("branch='{}'\n".format(GitBranch))
    ff.write("sha='{}'\n".format(GitHash))

define_macros=[("WITH_NUMERIC", "0"),
               ("FORTHON_PKGNAME", '\"FACEC\"'),
               ("FORTHON","1")]

# check for readline
rlncom = "echo \"int main(){}\" | gcc -x c -lreadline - "
rln = os.system(rlncom)
if rln == 0:
   define_macros = define_macros + [("HAS_READLINE","1")]
   os.environ["READLINE"] = "-l readline"
   libraries = ['readline'] + libraries


setup(name="pyface",
      version=get_version("pyface/__version__.py"),
      author='R. Smirnov/J. Guterl',
      author_email="guterlj@fusion.gat.com",
      description="pyFACE",
      packages=find_packages(include=['pyface']),
      # include_package_data=True,
      scripts=[],
       ext_modules=[Extension('pyface.FACEC',
                              ['src/FACEC_Forthon.c',
                               os.path.join(builddir, 'Forthon.c'),'src/wrapper.c'],
                              include_dirs=[builddir, numpy.get_include()],
                              library_dirs=library_dirs,
                              libraries=libraries,
                              define_macros=define_macros,
                              extra_objects=uedgeobjects,
                              extra_link_args=CARGS+['-g','-DFORTHON'] +
                              fcompiler.extra_link_args,
                              extra_compile_args=fcompiler.extra_compile_args
                              )],

      cmdclass={'build_ext': face_build, 'clean': face_clean},
      # note that include_dirs may have to be expanded in the line above
      classifiers=['Programming Language :: Python :: 3']
      )
