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

"""Handling CF grid mappings"""

__all__=['CFProj','CFProj_aea','CFProj_lcc','getCFProj','copyCFMap','CFProj_parse_GMTproj','CFProj_printGMThelp']

import Numeric
from PyCF import proj

class DummyProj:
    """Emptiy class for storing CF projection."""
    pass

class CFProj:
    def __init__(self,var):
        """Initialise.

        var: CF grid mapping variable."""
        self.params = {}
        self.params['proj'] = None
        try:
            self.params['x_0'] = var.false_easting[0]
        except:
            self.params['x_0'] = 0.
        try:
            self.params['y_0'] = var.false_westing[0]
        except:
            self.params['y_0'] = 0.
        self.gmt_type = ''

    def proj4_params(self):
        params = []
        for p in self.params.keys():
            params.append('%s=%s'%(p,self.params[p]))
        return params

    def proj4(self,point,inv=False):
        """Do projection.

        point: 2D point
        inv:   if True do the inverse projection."""

        projpt = proj.project(self.proj4_params(),Numeric.array([[point[0]],[point[1]]],Numeric.Float32),inv=inv)

        return [projpt[0,0], projpt[1,0]]

    def setOrigin(self,lon0,lat0):
        """Set origin of projected grid.

        lon0: Logitude of origin
        lat0: Latitude of origin."""

        orig = proj.project(self.proj4_params(),Numeric.array([[lon0],[lat0]],Numeric.Float32))
        self.params['x_0'] = -orig[0,0]
        self.params['y_0'] = -orig[1,0]

    def getGMTregion(self,ll,ur):
        """Get GMT region string.

        ll: coordinates of lower left corner in projected grid
        ur: coordinates of upper right corner in projected grid."""

        wesn = proj.project(self.proj4_params(),Numeric.array([[ll[0],ur[0]],[ll[1],ur[1]]],Numeric.Float32),inv=True)
        return '%f/%f/%f/%fr'%(wesn[0,0],wesn[1,0],wesn[0,1],wesn[1,1])

class CFProj_stere(CFProj):
    """Stereographic Projections."""

    def __init__(self,var):
        """Initialise.
        
        var: CF grid mapping variable."""
        CFProj.__init__(self,var)
        self.params['proj'] = 'stere'
        # polar variation
        if var.grid_mapping_name == 'polar_stereographic':
            self.params['lon_0'] = var.straight_vertical_longitude_from_pole[0]
            self.params['lat_0'] = 90.
        else: # others
            self.params['lat_0'] = var.latitude_of_projection_origin[0]
            self.params['lon_0'] = var.longitude_of_central_meridian[0]
        try:
            self.params['k_0'] = var.scale_factor_at_projection_origin[0]
        except AttributeError:
            self.params['k_0'] = 1.0
        self.gmt_type = 's'

    def getGMTprojection(self):
        """Get GMT projection string."""

        if 'k_0' in self.params:
            return '%s%f/%f/%f'%(self.gmt_type,
                              self.params['lon_0'],self.params['lat_0'],self.params['k_0'])
        else:
            return '%s%f/%f'%(self.gmt_type,
                              self.params['lon_0'],self.params['lat_0'])    
        
class CFProj_laea(CFProj):
    """Lambert Azimuthal Equal Area"""
    def __init__(self,var):
        """Initialise.
        
        var: CF grid mapping variable."""
        CFProj.__init__(self,var)
        self.params['proj'] = 'laea'
        self.params['lat_0'] = var.latitude_of_projection_origin[0]
        self.params['lon_0'] = var.longitude_of_central_meridian[0]
        self.gmt_type = 'a'

    def getGMTprojection(self):
        """Get GMT projection string."""

        return '%s%f/%f'%(self.gmt_type,
                                self.params['lon_0'],self.params['lat_0'])

class CFProj_aea(CFProj_laea):
    """Albers Equal-Area Conic."""

    def __init__(self,var):
        """Initialise.
        
        var: CF grid mapping variable."""
        CFProj_laea.__init__(self,var)
        self.params['lat_1'] = var.standard_parallel[0]
        if len(var.standard_parallel) == 2:
            self.params['lat_2'] = var.standard_parallel[1]
        if len(var.standard_parallel) < 1 or len(var.standard_parallel) > 2:
            raise RuntimeError, 'Wrong size of standard_parallel attribute'
        self.params['proj'] = 'aea'
        self.gmt_type = 'b'

    def getGMTprojection(self):
        """Get GMT projection string."""

        return '%s%f/%f/%f/%f'%(self.gmt_type,
                                self.params['lon_0'],self.params['lat_0'],
                                self.params['lat_1'],self.params['lat_2'])

class CFProj_lcc(CFProj_aea):
    """Lambert Conic Conformal."""

    def __init__(self,var):
        """Initialise.
        
        var: CF grid mapping variable."""
        CFProj_aea.__init__(self,var)
        self.params['proj'] = 'lcc'
        self.gmt_type = 'l'

def getCFProj(var):
    """Get projection from CF grid mapping variable.
    
    var: CF grid mapping variable."""
    
    CFProj_MAP = {'lambert_azimuthal_equal_area' : CFProj_laea,
                  'albers_conical_equal_area' : CFProj_aea,
                  'lambert_conformal_conic' : CFProj_lcc,
                  'polar_stereographic' : CFProj_stere,
                  'stereographic' : CFProj_stere}

    if var.grid_mapping_name not in CFProj_MAP:
        raise KeyError, 'Error, no idea how to handle projection: %s'%var.grid_mapping_name

    return CFProj_MAP[var.grid_mapping_name](var)

def copyCFMap(orig,copy):
    """Copy CF mapping variable."""

    if 'grid_mapping_name' in dir(orig):
        copy.grid_mapping_name = orig.grid_mapping_name
    if 'standard_parallel' in dir(orig):
        copy.standard_parallel = orig.standard_parallel
    if 'longitude_of_central_meridian' in dir(orig):
        copy.longitude_of_central_meridian = orig.longitude_of_central_meridian
    if 'latitude_of_projection_origin' in dir(orig):
        copy.latitude_of_projection_origin = orig.latitude_of_projection_origin
    if 'false_easting' in dir(orig):
        copy.false_easting = orig.false_easting
    if 'false_westing' in dir(orig):
        copy.false_westing = orig.false_westing
    if 'straight_vertical_longitude_from_pole' in dir(orig):
        copy.straight_vertical_longitude_from_pole = orig.straight_vertical_longitude_from_pole
    if '' in dir(orig):
        copy.scale_factor_at_projection_origin = orig.scale_factor_at_projection_origin

def CFProj_parse_GMTproj(projstring):
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
    elif projstring[0] in ['a','A']:
        if len(ps) != 2:
            print 'Error, wrong number of projection arguments'
            usage()
            sys.exit(1)
        proj.grid_mapping_name='lambert_azimuthal_equal_area'
        proj.longitude_of_central_meridian = [float(ps[0])]
        proj.latitude_of_projection_origin = [float(ps[1])]
    elif projstring[0] in ['s','S']:
        if len(ps) == 2 or len(ps) == 3:
            proj.grid_mapping_name='stereographic'
            proj.longitude_of_central_meridian = [float(ps[0])]
            proj.latitude_of_projection_origin = [float(ps[1])]
            if len(ps) == 3:
                proj.scale_factor_at_projection_origin = [float(ps[2])]
            else:
                proj.scale_factor_at_projection_origin = [1.]
        else:
            print 'Error, wrong number of projection arguments'
            usage()
            sys.exit(1)
    else:
        print 'Error, no idea about projection: ',projstring
        usage()
        sys.exit(1)
    return proj

def CFProj_printGMThelp():
    print '  -Jspec\n\tGMT like projection specification'
    print '\t  -Jalon0/lat0\n\t      Lambert Azimuthal Equal Area. Give projection center'
    print '\t  -Jblon0/lat0/lat1/lat2\n\t      Albers Equal-Area Conic. Give projection center and\n\t      two  standard  parallels.'
    print '\t  -Jllon0/lat0/lat1/lat2\n\t      Lambert Conic Conformal. Give projection center and\n\t      two  standard  parallels.'
    print '\t  -Jslon0/lat0[/scale]\n\t      Stereographic projection. Give projection center and\n\t      optionally scale at projection center.'
