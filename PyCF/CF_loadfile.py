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

"""Loading CF files."""

__all__=['CFloadfile','CFvariable']

import Numeric, Scientific.IO.NetCDF,os
from PyGMT.PyGMTgrid import Grid
from CF_proj import *
from CF_colourmap import *

class CFloadfile(object):
    """Loading a CF netCDF file."""

    def __init__(self,fname):
        """Initialise.

        fname: name of CF file."""

        self.file = Scientific.IO.NetCDF.NetCDFFile(fname,'r')
        self.title = os.path.basename(fname)
        self.timescale = 0.001

        self.projection = self.__get_projection()
        self.__ll_xy_changed = False
        self.__ll_xy = [self.file.variables['x1'][0],self.file.variables['y1'][0]]
        self.__ll_geo = self.projection.proj4(self.__ll_xy,inv=True)
        self.__ur_xy_changed = False
        self.__ur_xy = [self.file.variables['x1'][-1],self.file.variables['y1'][-1]]
        self.__ur_geo = self.projection.proj4(self.__ur_xy,inv=True)
        
    # lower left corner in projected coordinates
    def __get_ll_xy(self):
        return self.__ll_xy
    def __set_ll_xy(self,val):
        if self.inside(val):
            self.__ll_xy = val
            self.__ll_xy_changed = True
        else:
            raise RuntimeError, 'Point outside grid'
    ll_xy = property(__get_ll_xy,__set_ll_xy)
    # and geographic coordinates
    def __get_ll_geo(self):
        if self.__ll_xy_changed:
            self.__ll_geo = self.projection.proj4(self.__ll_xy,inv=True)
        return self.__ll_geo
    def __set_ll_geo(self,val):
        self.__set_ll_xy(self.projection.proj4(val))
        self.__ll_xy_changed = False
        self.__ll_geo = val
    ll_geo = property(__get_ll_geo,__set_ll_geo)

    #  upper right corner in projected coordinates
    def __get_ur_xy(self):
        return self.__ur_xy
    def __set_ur_xy(self,val):
        if self.inside(val):
            self.__ur_xy = val
            self.__ur_xy_changed = True
        else:
            raise RuntimeError, 'Point outside grid'
    ur_xy = property(__get_ur_xy,__set_ur_xy)
    # and geographic coordinates
    def __get_ur_geo(self):
        if self.__ur_xy_changed:
            self.__ur_geo = self.projection.proj4(self.__ur_xy,inv=True)
        return self.__ur_geo
    def __set_ur_geo(self,val):
        self.__set_ur_xy(self.projection.proj4(val))
        self.__ur_xy_changed = False
        self.__ur_geo = val
    ur_geo = property(__get_ur_geo,__set_ur_geo)
    
    # get projection info
    def __get_projection(self):
        for var in self.file.variables.keys():
            if hasattr(self.file.variables[var],'grid_mapping_name'):
                return getCFProj(self.file.variables[var])
        return None

    def time(self,t):
        """Return selected time value."""
        return float(self.file.variables['time'][t])*self.timescale

    def timeslice(self,time,round='n'):
        """Get the time slice.

        time: time to look up in ISM file
        round: 'n' round to nearest
               'u' round up
               'd' round down"""

        if round not in ['n','u','d']:
            raise ValueError, "Expected one of 'n', 'u', 'd'"

        t0 = 0
        t1 = len(self.file.variables['time'][:])-1
        if time < self.time(t0) or time > self.time(t1):
            raise ValueError, 'Selected time slice [%f] is outside file: [%f, %f]'%(time,self.time(t0),self.time(t1))
        if time == self.time(t0): return t0
        if time == self.time(t1): return t1
        # use Newton bisection
        tmid = int((t1-t0)/2)
        while tmid > 0:
            if time < self.time(t0+tmid):
                t1 = t0+tmid
            elif time > self.time(t0+tmid):
                t0 = t0+tmid
            else:
                return t0+tmid
            tmid = int((t1-t0)/2)
        if round == 'u':
            return t1
        elif round == 'd':
            return t0
        else:
            if (time-self.time(t0)) < (self.time(t1) - time):
                return t0
            else:
                return t1
        raise AssertionError, 'Why are we here?'

    def inside(self, point):
        """Check if point is inside data set."""

        result = (point[0] >= self.file.variables['x1'][0] and point[0] <= self.file.variables['x1'][-1] and
                  point[1] >= self.file.variables['y1'][0] and point[1] <= self.file.variables['y1'][-1])
        return result

class CFvariable(object):
    """Handling CF variables."""

    def __init__(self,CFfile,var):
        """Initialise.

        CFFile: CF file
        var: name of variable"""

        self.CFfile = CFfile
        self.file = CFfile.file
        self.name = var
        if var not in self.file.variables.keys():
            raise KeyError, 'Variable not in file'
        self.var = self.file.variables[var]
        self.__colourmap = CFcolourmap(self)

    def __get_units(self):
        try:
            return self.var.units
        except:
            return ''
    units = property(__get_units)

    def __get_long_name(self):
        try:
            return self.var.long_name
        except:
            return ''
    long_name = property(__get_long_name)

    def __get_standard_name(self):
        try:
            return self.var.standard_name
        except:
            return ''
    standard_name = property(__get_standard_name)

    def __get_xdim(self):
        return self.file.variables[self.var.dimensions[-1]]
    xdim = property(__get_xdim)

    def __get_ydim(self):
        return self.file.variables[self.var.dimensions[-2]]
    ydim = property(__get_ydim)

    def __get_colourmap(self):
        return self.__colourmap
    def __set_colourmap(self,name):
        self.__colourmap = CFcolourmap(self,filename=name)
    colourmap = property(__get_colourmap,__set_colourmap)
    
    def get2Dfield(self,time,level=0):
        """Get a 2D field.

        time: time slice
        level: horizontal slice."""

        if len(self.var.shape) is 4:
            grid = Numeric.transpose(self.var[time,level,:,:])
        else:
            grid = Numeric.transpose(self.var[time,:,:])
        return grid

    def getGMTgrid(self,time,level=0):
        """Get a GMT grid.

        time: time slice
        level: horizontal slice."""

        grid = Grid()
        grid.zunits = self.units
        grid.remark = self.long_name
        
        # setting min/max of coords
        grid.x_minmax = [self.xdim[0],self.xdim[-1]]
        grid.y_minmax = [self.ydim[0],self.ydim[-1]]
    
        if (time >= len(self.file.variables['time'][:])):
            raise ValueError, 'ISM file does not contain time slice %d' % time

        grid.data = self.get2Dfield(time,level)
        
        return grid
