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

import sys,getopt,PyCF,PyGMT,Numeric,Scientific.IO.NetCDF,datetime

def usage():
    "print short help message"

    print 'Usage: create_topo.py [OPTIONS] infile outfile'
    print 'create CF topography from long/lat ncdf file.'
    print ''
    print '  -h, --help\n\tthis message'
    print '  -Jspec\n\tGMT like projection specification'
    print '\t  -Jblon0/lat0/lat1/lat2\n\t    Albers Equal-Area Conic. Give projection  center and  two  standard  parallels.'
    print '\t  -Jllon0/lat0/lat1/lat2\n\t    Lambert Conic Conformal. Give projection  center and  two  standard  parallels.'
    print '  -o, --origin lon/lat\n\tLongitude and latitude of origin of the projected coordinate system.'
    print '  -d, --delta dx[/dy]\n\tNode spacing. Assume dx==dy if dy is omitted.'
    print '  -n, --num x/y\n\tGrid size.'
    print '  --title\n\t title for output netCDF file'
    print '  --institution\n\tname of institution'
    print '  --source\n\tdata source'
    print '  --references\n\tsome references'
    print '  --comment\n\tcomment'

class DummyProj:
    """Emptiy class for storing CF projection."""
    pass

def parse_GMTproj(projstring):
    """Parse GMT projection string."""

    proj = DummyProj()
    
    ps = projstring[1:].split('/')
    if projstring[0] in ['b','B']:
        if len(ps) != 4:
            print 'Error, wrong number of projection arguments'
            usage()
            sys.exit(1)
        proj.grid_mapping_name='albers_conical_equal_area'
        proj.longitude_of_central_meridian = [float(ps[0])]
        proj.latitude_of_projection_origin = [float(ps[1])]
        proj.standard_parallel = [float(ps[2]),float(ps[3])]
    elif projstring[0] in ['l','L']:
        if len(ps) != 4:
            print 'Error, wrong number of projection arguments'
            usage()
            sys.exit(1)
        proj.grid_mapping_name='lambert_conformal_conic'
        proj.longitude_of_central_meridian = [float(ps[0])]
        proj.latitude_of_projection_origin = [float(ps[1])]
        proj.standard_parallel = [float(ps[2]),float(ps[3])]
    else:
        print 'Error, no idea about projection: ',projstring
        usage()
        sys.exit(1)
    return proj

def read_global_topo(filename):
    ncfile = Scientific.IO.NetCDF.NetCDFFile(filename,'r')
        
    for var in ['topography','latitude','longitude']:
        if var not in ncfile.variables.keys():
            raise LookupError, '%s not in file %s'%(var,filename)

    topo = PyGMT.Grid()
    topo.y_minmax=[ncfile.variables['latitude'][0],ncfile.variables['latitude'][-1]]
    topo.x_minmax=[ncfile.variables['longitude'][0],ncfile.variables['longitude'][-1]]
    topo.data = Numeric.transpose(ncfile.variables['topography'][:,:])

    ncfile.close()

    return topo
        
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
            proj = parse_GMTproj(a)
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
    proj.false_westing = proj4.params['y_0']
    
    # loading topography
    globtopo = read_global_topo(inname)

    # projecting topography
    proj_gmt='-J%s/1:1 -R%s -A -D%f/%f'%(
        proj4.getGMTprojection(),
        proj4.getGMTregion([0.,0.],[delta[0]*num[0],delta[1]*num[1]]),
        delta[0],delta[1])
    projtopo = globtopo.project(proj_gmt)

    (numx,numy) = projtopo.data.shape    

    # creating output netCDF file
    ncfile = Scientific.IO.NetCDF.NetCDFFile(outname,'w')
    # global attributes
    ncfile.Conventions = "CF-1.0"
    if title is not None:
        ncfile.title = title
    if institution is not None:
        ncfile.institution = institution
    if source  is not None:
        ncfile.source = source
    args = ''
    for a in sys.argv:
        args = args + '%s '%a
    ncfile.history = '%s: %s'%(datetime.datetime.today(),args)
    if references  is not None:
        ncfile.references=references
    if comment is not None:
        ncfile.comment = comment

    # creating dimensions
    ncfile.createDimension('x1',numx)
    ncfile.createDimension('y1',numy)
    ncfile.createDimension('time',None)
    #creating variables
    varx=ncfile.createVariable('x1',Numeric.Float32,('x1',))
    varx.units = "meter"
    varx.long_name = "Cartisian x-coordinate"
    varx[:] = (delta[0]*Numeric.arange(numx)).astype(Numeric.Float32)

    vary=ncfile.createVariable('y1',Numeric.Float32,('y1',))
    vary.units = "meter"
    vary.long_name = "Cartisian y-coordinate"
    vary[:] = (delta[1]*Numeric.arange(numy)).astype(Numeric.Float32)

    vartime=ncfile.createVariable('time',Numeric.Int,('time',))
    vartime.long_name = "Model Time"
    vartime.units = "year"
    vartime[0] = 0

    varmap=ncfile.createVariable('mapping','c',())
    PyCF.copyCFMap(proj,varmap)

    varlat=ncfile.createVariable('lat',Numeric.Float32,('time', 'y1', 'x1'))
    varlat.units = "degreeN"
    varlat.long_name = "Latitude"
    varlat.grid_mapping = 'mapping'

    varlong=ncfile.createVariable('lon',Numeric.Float32,('time', 'y1', 'x1'))
    varlong.units = "degreeE"
    varlong.long_name = "Longitude"
    varlong.grid_mapping = 'mapping'

    vartopg=ncfile.createVariable('topg',Numeric.Float32,('time', 'y1', 'x1'))
    vartopg.long_name = "bedrock topography"
    vartopg.units = "meter"
    vartopg.grid_mapping = 'mapping'

    # get long/lat
    longs = varlong[0,:,:]
    lats = varlat[0,:,:]
    for i in range(0,numy):
        longs[i,:] = varx[:]
    for i in range(0,numx):
        lats[:,i] = vary[:]
    lats.shape = (numx*numy,)
    longs.shape = (numx*numy,)
    coords = Numeric.array([longs,lats])
    coords = PyCF.project(proj4.proj4_params(),coords,inv=True)
    longs = coords[0,:]
    lats = coords[1,:]
    lats.shape = (numy,numx)
    longs.shape = (numy,numx)    
    varlong[0,:,:] = longs[:,:]
    varlat[0,:,:] = lats[:,:]

    vartopg[0,:,:] =  Numeric.transpose(projtopo.data[:,:]).astype(Numeric.Float32)

    ncfile.close()
