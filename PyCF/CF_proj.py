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

__all__=['CFProj','CFProj_aea','CFProj_lcc','getCFProj','copyCFMap']

import proj, Numeric

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

class CFProj_aea(CFProj):
    """Albers Equal-Area Conic."""

    def __init__(self,var):
        """Initialise.
        
        var: CF grid mapping variable."""
        CFProj.__init__(self,var)
        self.params['proj'] = 'aea'
        self.params['lat_1'] = var.standard_parallel[0]
        if len(var.standard_parallel) == 2:
            self.params['lat_2'] = var.standard_parallel[1]
        if len(var.standard_parallel) < 1 or len(var.standard_parallel) > 2:
            raise RuntimeError, 'Wrong size of standard_parallel attribute'
        self.params['lat_0'] = var.latitude_of_projection_origin[0]
        self.params['lon_0'] = var.longitude_of_central_meridian[0]
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
    
    CFProj_MAP = {'albers_conical_equal_area' : CFProj_aea, 'lambert_conformal_conic' : CFProj_lcc}

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

        
