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

import sys,getopt,PyCF,PyGMT,Numeric,datetime,os, RandomArray

def usage():
    "print short help message"

    print 'Usage: ran_topo.py [OPTIONS] outfile'
    print 'create a random CF topography file\n Specify number of nodes and the amplitude.' 
    print ''
    print '  -h, --help\n\tthis message'
    print '  -d, --delta dx[/dy]\n\tNode spacing. Assume dx==dy if dy is omitted. [default: 25000]'
    print '  -n, --num x/y\n\tGrid size. [default: 61/61]'
    print '  -a, --amplitude a\n\tAmplitude of random topo. [default: 10]'
    print '  --title\n\t title for output netCDF file'
    print '  --institution\n\tname of institution'
    print '  --references\n\tsome references'
    print '  --comment\n\tcomment'
        
if __name__ == '__main__':

    # get options
    try:
        opts, args = getopt.getopt(sys.argv[1:],'hd:n:a:',['help','delta=','num=','amplitude=','title=','institution=','references=','comment='])
    except getopt.GetoptError,error:
        # print usage and exit
        print error
        usage()
        sys.exit(1)

    if len(args) == 1:
        outname = args[0]
    else:
        usage()
        sys.exit(1)

    delta = [25000.,25000.]
    num = [61,61]
    amplitude = 10.
    title='Random Topo'
    institution=None
    references=None
    comment=None
    for o,a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit(0)
        if o in ('-d','--delta'):
            a = a.split('/')
            if len(a)==1:
                delta = [float(a[0]),float(a[0])]
            elif len(a)==2:
                delta = [float(a[0]),float(a[1])]
            else:
                print 'Error, cannot parse delta string'
                usage()
                sys.exit(1)
        if o in ('-n','--num'):
            a = a.split('/')
            try:
                num = [int(a[0]),int(a[1])]
            except:
                print 'Error, cannot parse num string'
                usage()
                sys.exit(1)
        if o in ('-a','--amplitude'):
            amplitude = float(a)
        if o == '--title':
            title = a
        if o == '--institution':
            institution = a
        if o == '--references':
            references = a
        if o == '--comment':
           comment  = a
        


    numx = num[0]
    numy = num[1]
    
    # creating output netCDF file
    cffile = PyCF.CFcreatefile(outname)
    # global attributes
    if title is not None:
        cffile.title = title
    if institution is not None:
        cffile.institution = institution
    args = ''
    for a in sys.argv:
        args = args + '%s '%a
    cffile.history = '%s: %s'%(datetime.datetime.today(),args)
    if references  is not None:
        cffile.references=references
    if comment is not None:
        cffile.comment = comment

    # creating dimensions
    cffile.createDimension('x0',numx-1)
    cffile.createDimension('x1',numx)
    cffile.createDimension('y0',numy-1)
    cffile.createDimension('y1',numy)
    cffile.createDimension('level',1)
    cffile.createDimension('time',None)
    #creating variables
    varx=cffile.createVariable('x0')
    varx[:] = (delta[0]*Numeric.arange(numx-1)).astype(Numeric.Float32)
    varx=cffile.createVariable('x1')
    varx[:] = (delta[0]*Numeric.arange(numx)).astype(Numeric.Float32)

    vary=cffile.createVariable('y0')
    vary[:] = (delta[1]*Numeric.arange(numy-1)).astype(Numeric.Float32)
    vary=cffile.createVariable('y1')
    vary[:] = (delta[1]*Numeric.arange(numy)).astype(Numeric.Float32)

    varlevel=cffile.createVariable('level')
    varlevel[0] = 1

    vartime=cffile.createVariable('time')
    vartime[0] = 0

    vartopg=cffile.createVariable('topg')



    vartopg[0,:,:] = RandomArray.uniform(0.,amplitude,(numy,numx)).astype(Numeric.Float32)

    
    cffile.close()
