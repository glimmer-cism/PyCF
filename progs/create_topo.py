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

import sys,getopt,PyCF,PyGMT,Numeric,datetime,os

def usage():
    "print short help message"

    print 'Usage: create_topo.py [OPTIONS] infile outfile'
    print 'create CF topography from a GMT grid file'
    print ''
    print '  -h, --help\n\tthis message'
    PyCF.CFProj_printGMThelp()
    print '  -o, --origin lon/lat\n\tLongitude and latitude of origin of the projected coordinate system.'
    print '  -d, --delta dx[/dy]\n\tNode spacing. Assume dx==dy if dy is omitted.'
    print '  -n, --num x/y\n\tGrid size.'
    print '  --title\n\t title for output netCDF file'
    print '  --institution\n\tname of institution'
    print '  --source\n\tdata source'
    print '  --references\n\tsome references'
    print '  --comment\n\tcomment'
        
if __name__ == '__main__':

    # get options
    try:
        opts, args = getopt.getopt(sys.argv[1:],'hJ:o:d:n:',['help','origin=','delta=','num=','title=','institution=','source=','references=','comment='])
    except getopt.GetoptError:
        # print usage and exit
        usage()
        sys.exit(1)

    if len(args) == 2:
        inname = args[0]
        outname = args[1]
    else:
        usage()
        sys.exit(1)

    proj = None
    origin = None
    delta = None
    num = None
    title=None
    institution=None
    source=None
    references=None
    comment=None
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
        if o == '--title':
            title = a
        if o == '--institution':
            institution = a
        if o == '--source':
            source  = a
        if o == '--references':
            references = a
        if o == '--comment':
           comment  = a
        

    if proj is None or origin is None or delta is None or num is None:
        usage()
        sys.exit(1)

    proj4 = PyCF.getCFProj(proj)
    proj4.setOrigin(origin[0],origin[1])
    proj.false_easting = proj4.params['x_0']
    proj.false_northing = proj4.params['y_0']
    # projecting topography
    proj_gmt='-J%s/1:1 -R%s -A -D%f/%f'%(
        proj4.getGMTprojection(),
        proj4.getGMTregion([0.,0.],[delta[0]*num[0],delta[1]*num[1]]),
        delta[0],delta[1])

    PyGMT.command('grdproject','%s -G.__temp=1 %s'%(inname,proj_gmt))

    projfile = open('.__temp')
    projtopo = PyGMT.read_grid(projfile)
    projfile.close()
    os.remove('.__temp')

    (numx,numy) = projtopo.data.shape    
    
    # creating output netCDF file
    cffile = PyCF.CFcreatefile(outname)
    # global attributes
    if title is not None:
        cffile.title = title
    if institution is not None:
        cffile.institution = institution
    if source  is not None:
        cffile.source = source
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

    cffile.projection=proj

    varlat=cffile.createVariable('lat')

    varlong=cffile.createVariable('lon')

    vartopg=cffile.createVariable('topg')

    # get long/lat
    longs = varlong[0,:,:]
    lats = varlat[0,:,:]
    for i in range(0,numy):
        longs[i,:] = varx[:]
    for i in range(0,numx):
        lats[:,i] = vary[:]

    projection = PyCF.Proj(proj4.proj4_params())
    lats.shape = (numx*numy,)
    longs.shape = (numx*numy,)
    (longs,lats) = projection.gridinv((longs,lats))
    lats.shape = (numy,numx)
    longs.shape = (numy,numx)
    varlong[0,:,:] = longs[:,:].astype(Numeric.Float32)
    varlat[0,:,:] = lats[:,:].astype(Numeric.Float32)

    vartopg[0,:,:] =  Numeric.transpose(projtopo.data[:,:]).astype(Numeric.Float32)

    cffile.close()
