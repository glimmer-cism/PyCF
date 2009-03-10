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

import sys,getopt,PyCF,PyGMT,numpy,datetime,os, numpy.random

def usage():
    "print short help message"

    print 'Usage: ran_topo.py [OPTIONS] outfile'
    print 'create a random CF topography file\n Specify number of nodes and the amplitude.' 
    print ''
    print '  -h, --help\n\tthis message'
    print '  -d, --delta dx[/dy]\n\tNode spacing. Assume dx==dy if dy is omitted. [default: 25000]'
    print '  -n, --num x/y\n\tGrid size. [default: 61/61]'
    print '  -a, --amplitude a\n\tAmplitude of random topo. [default: 10]'
    print '  -y, --yprofile name\n\tname of file containing profile in y-dir. (default none)'
    print '  --long\n\tset longitude (default none)'
    print '  --lat\n\tset latitude (default none)'
    print '  --title\n\t title for output netCDF file'
    print '  --institution\n\tname of institution'
    print '  --references\n\tsome references'
    print '  --comment\n\tcomment'
        
if __name__ == '__main__':

    # get options
    try:
        opts, args = getopt.getopt(sys.argv[1:],'hd:n:a:y:',['help','delta=','num=','amplitude=','title=','institution=','references=','comment=','yprofile=','long=','lat='])
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
    yprof=None
    long = None
    lat = None
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
        if o in ('-y','--yprofile'):
            yprof = open(a)
        if o == '--long':
            long = float(a)
        if o == '--lat':
            lat = float(a)
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
    varx[:] = (delta[0]*numpy.arange(numx-1)).astype('f')
    varx=cffile.createVariable('x1')
    varx[:] = (delta[0]*numpy.arange(numx)).astype('f')

    vary=cffile.createVariable('y0')
    vary[:] = (delta[1]*numpy.arange(numy-1)).astype('f')
    vary=cffile.createVariable('y1')
    vary[:] = (delta[1]*numpy.arange(numy)).astype('f')

    varlevel=cffile.createVariable('level')
    varlevel[0] = 1

    vartime=cffile.createVariable('time')
    vartime[0] = 0

    vartopg=cffile.createVariable('topg')

    if long!=None:
        vlong = cffile.createVariable('lon')
        vlong[0,:,:] = long
    if lat!=None:
        vlat = cffile.createVariable('lat')
        vlat[0,:,:] = lat
    

    if yprof != None:
        x = []
        y = []
        for l in yprof.readlines():
            l = l.split()
            x.append(float(l[0]))
            y.append(float(l[1]))
        i = 0
        while  i*delta[1]<=x[0]:
            vartopg[0,i,:] = y[0]
            i = i + 1
            if i == numx:
                break
        for d in range(0,len(x)-1):
            slope = (y[d+1]-y[d])/(x[d+1]-x[d])
            if i == numx:
                break
            while  i*delta[1]<=x[d+1]:
                vartopg[0,i,:] = y[d]+(i*delta[1]-x[d])*slope
                i = i + 1
                if i == numx:
                    break
        for i in range(i,numx):
            vartopg[0,i,:] = y[d]
        
    else:
        vartopg[0,:,:] = 0.

    vartopg[0,:,:] = vartopg[0,:,:] + numpy.random.uniform(0.,amplitude,(numy,numx)).astype('f')

    
    cffile.close()
