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
from CF_file import *

temperatures = ['btemp','temp']

def CFchecklist(section,variable):
    """Check if section is a list.

    if variable is a None,     return (True,[0,len(variable)-1])
    if variable is a list/etc, return (True,[section[0],section[1]])
    if variable is a value,    return (False,val) """

    if section is None:
        return (True, [0,len(variable)-1])
    elif type(section) == list or type(section) == tuple or type(section) == Numeric.ArrayType:
        return (True, [section[0],section[1]])
    else:
        return (False,section)

class CFloadfile(CFfile):
    """Loading a CF netCDF file."""

    def __init__(self,fname):
        """Initialise.

        fname: name of CF file."""

        CFfile.__init__(self,fname)

        self.file = Scientific.IO.NetCDF.NetCDFFile(self.fname,'r')
        self.timescale = 0.001
        # get mapping variable name
        for var in self.file.variables.keys():
            if hasattr(self.file.variables[var],'grid_mapping_name'):
                self.mapvarname = var
                break
        self.reset_bb()

    def time(self,t):
        """Return selected time value."""

        (isar,sel) = CFchecklist(t,self.file.variables['time'])

        if isar:
            return self.file.variables['time'][sel[0]:sel[1]]*self.timescale
        else:
            return self.file.variables['time'][sel]*self.timescale

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
        self.pmt = False

    def __get_units(self):
        try:
            return self.var.units
        except:
            return ''
    units = property(__get_units)

    def __get_long_name(self):
        try:
            if self.name in temperatures and self.pmt and 'thk' in self.file.variables.keys():
                return 'homologous %s'%self.var.long_name
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
        if self.name == 'topg':
            if 'eus' in self.file.variables.keys():
                grid = grid + self.file.variables['eus'][time]
        # correct temperature
        if self.name in temperatures:
            if self.pmt:
                if 'thk' not in self.file.variables.keys():
                    print 'Warning, cannot correct for pmt because ice thicknesses are not in file'
                else:
                    ih = Numeric.transpose(self.file.variables['thk'][time,:,:])
                    grid = grid + 8.7e-4*ih
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

    def getSpotIJ(self,node,time=None,level=0):
        """Get data at a grid node.

        node: list/tuple/array of size 2 selecting node
        time: if None, return data for all time slices
              if list/etc of size two, interpret as array selection
              if single value, get only this time slice
        level: if None get data for all levels (time must be a single value)
               otherwise get a specific level"""

        if node[0] < 0 or node[0] >= len(self.xdim) or node[1] < 0 or node[1] >= len(self.ydim):
            raise RuntimeError, 'node is outside bounds'

        (tarray,t) = CFchecklist(time,self.file.variables['time'])
        (larray,l) = CFchecklist(level,self.file.variables['level'])

        if 'level' not in self.var.dimensions:
            larray = False
            l = 0

        if larray and tarray:
            raise RuntimeError, 'Cannot select both multiple times and vertical slices'

        values = []
        if tarray:
            for i in range(t[0],t[1]+1):
                values.append(self.get2Dfield(i,l)[node[0],node[1]])
            return values
        if larray:
            for i in range(l[0],l[1]+1):
                values.append(self.get2Dfield(t,i)[node[0],node[1]])
            return values

        return self.get2Dfield(t,l)[node[0],node[1]]
        
