#!/usr/bin/env python

from distutils.core import setup, Extension
import os, sys

def check_lib(libname,prefix_var,header):
    """Check if we can find header either in the directory where the environment
    variable prefix_var points to, or /usr/local or /usr."""

    prefix = []

    try:
        prefix.append(os.environ[prefix_var])        
    except KeyError:
        for p in ['/usr/local', '/usr']:
            prefix.append(p)
    for p in prefix:
        include = os.path.join(p, 'include')
        lib = os.path.join(p, 'lib')
        if os.path.exists(os.path.join(include, header)):
            break
    else:
        print 'Error, cannot find %s library in /usr/local and /usr.'%libname
        print 'Set environment variable %s to point to the prefix'%prefix_var
        print 'where %s is installed.'%libname
        sys.exit(1)
    return (include,lib)


(proj_include, proj_lib) = check_lib('proj4','PROJ_PREFIX','projects.h')
(gsl_include, gsl_lib)   = check_lib('GSL', 'GSL_PREFIX', 'gsl/gsl_errno.h')

print
print 'Configuration'
print '-------------'
print 'proj4: %s, %s'%(proj_include, proj_lib)
print 'GSL:   %s, %s'%(gsl_include, gsl_lib)
print

ext_modules = [
    Extension('PyCF.proj',
              ['src/projmodule.c'],
              include_dirs=[proj_include],
              library_dirs=[proj_lib],
              libraries = ['proj']),
    Extension('PyCF.TwoDspline',
              ['src/2Dsplinemodule.c'],
              include_dirs=[gsl_include],
              library_dirs=[gsl_lib],
              libraries = ['gsl','gslcblas']),
    ]
data_files = [('share/PyCF/',['data/ice.cpt',
                              'data/mb.cpt',
                              'data/temp.cpt',
                              'data/surf_temp.cpt',
                              'data/topo.cpt',
                              'data/velo.cpt',
                              'data/gthf.cpt',
                              'data/litho_temp.cpt',
                              'data/rsl_res.cpt',
                              'data/eismint2.data']),
              ('bin',['progs/add_projinfo.py',
                      'progs/create_topo.py',
                      'progs/construct_field.py',
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
                      'progs/plotRSLloc.py',
                      'progs/plotRSLhist.py',
                      'progs/plotRSLdata.py',
                      'progs/plotRSLres.py',
		      'progs/extractCFstats.py',
                      'progs/ran_topo.py',
		      'progs/extractTS.py',
                      'progs/plotStreams.py',
                      'progs/plotCFdiff.py',
                      'progs/plot_extent.py',
                      'progs/a2c.py',
                      'progs/plotEISMINT2stats.py'])]

setup (name = "PyCF",
       version = "0.4",
       description = "Python modules for CF",
       author = "Magnus Hagdorn",
       author_email = "Magnus.Hagdorn@ed.ac.uk",
       packages = ['PyCF'],
       ext_modules = ext_modules,
       data_files=data_files,
       )



#EOF
