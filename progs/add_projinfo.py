#!/usr/bin/env python

# Copyright 2004, Magnus Hagdorn
# 
# This file is part of GLIMMER.
# 
# GLIMMER is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# GLIMMER is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GLIMMER; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import sys,getopt,PyCF,os,Scientific.IO.NetCDF

def usage():
    "print short help message"

    print 'Usage: add_projinfo.py [OPTIONS] file'
    print 'add projection info the netCDF file'
    print ''
    print '  -h, --help\n\tthis message'
    PyCF.CFProj_printGMThelp()
    print '  -o, --origin lon/lat\n\tLongitude and latitude of origin of the projected coordinate system.'

if __name__ == '__main__':

    # get options
    try:
        opts, args = getopt.getopt(sys.argv[1:],'hJ:o:',['help','origin='])
    except getopt.GetoptError:
        # print usage and exit
        usage()
        sys.exit(1)

    if len(args) == 1:
        inname = args[0]
    else:
        usage()
        sys.exit(1)

    proj = None
    origin = None
    for o,a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit(0)
        if o == '-J':
            proj = PyCF.CFProj_parse_GMTproj(a)
        if o in ('-o', '--origin'):
            a = a.split('/')
            try:
                origin = [float(a[0]),float(a[1])]
            except:
                print 'Error, cannot parse origin string'
                usage()
                sys.exit(1)

        

    if proj is None or origin is None:
        usage()
        sys.exit(1)

    proj4 = PyCF.getCFProj(proj)
    proj4.setOrigin(origin[0],origin[1])
    proj.false_easting = proj4.params['x_0']
    proj.false_northing = proj4.params['y_0']
    
    cffile = Scientific.IO.NetCDF.NetCDFFile(inname,'r+')

    if 'mapping' in cffile.variables.keys():
        print 'netCDF file already got map projection info.'
        sys.exit(0)

    varmap=cffile.createVariable('mapping','c',())
    PyCF.copyCFMap(proj,varmap)

    for var in cffile.variables.keys():
        if 'x1' in cffile.variables[var].dimensions and 'y1' in cffile.variables[var].dimensions:
            cffile.variables[var].grid_mapping = 'mapping'

    cffile.close()

        
