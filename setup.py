#!/usr/bin/env python

from distutils.core import setup, Extension
import os, sys

proj_prefix = None

if proj_prefix is None:
    try:
        proj_prefix=os.environ['PROJ_PREFIX']
    except KeyError:
        for proj_prefix in ['/usr/local', '/usr']:
            proj_include = os.path.join(proj_prefix, 'include')
            proj_lib = os.path.join(proj_prefix, 'lib')
            if os.path.exists(os.path.join(proj_include, 'projects.h')):
                break
        else:
            proj_prefix = None
if proj_prefix is None:
    raise RuntimeError, 'Cannot find proj4 library in /usr/local and /usr'
else:
    proj_include = os.path.join(proj_prefix, 'include')
    proj_lib = os.path.join(proj_prefix, 'lib')


ext_modules = [
    Extension('PyCF.proj',
              ['src/projmodule.c'],
              include_dirs=[proj_include],
              library_dirs=[proj_lib],
              libraries = ['proj']),
    ]
data_files = [('share/PyCF/',['data/ice.cpt',
                              'data/mb.cpt',
                              'data/temp.cpt',
                              'data/topo.cpt',
                              'data/velo.cpt',
                              'data/eismint2.data']),
              ('bin',['progs/add_projinfo.py',
                      'progs/create_topo.py',
                      'progs/plotCFvar.py',
                      'progs/plotEISvar.py',
                      'progs/plotEISMINT.py',
                      'progs/plotSpot.py',
                      'progs/plotProfile.py',
		      'progs/plotProfileTS.py',
                      'progs/plot3DProfiles.py',
                      'progs/plotCFstats.py',
                      'progs/extractProfile.py',
                      'progs/extract3DProfile.py',
                      'progs/plotRSL.py',
		      'progs/extractCFstats.py',
                      'progs/ran_topo.py',
		      'progs/extractTS.py',
                      'progs/plotStreams.py',
                      'progs/plotCFdiff.py',
                      'progs/plotEISMINT2stats.py'])]

setup (name = "PyCF",
       version = "0.2",
       description = "Python modules for CF",
       author = "Magnus Hagdorn",
       author_email = "Magnus.Hagdorn@ed.ac.uk",
       packages = ['PyCF'],
       ext_modules = ext_modules,
       data_files=data_files,
       )



#EOF
