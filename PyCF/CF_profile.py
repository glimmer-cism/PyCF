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

"""Loading CF profiles files."""

__all__=['CFloadprofile']

import Numeric
from CF_loadfile import *
from CF_utils import CFinterpolate_xy

class CFloadprofile(CFloadfile):
    """Loading a profile line from a CF netCDF file."""

    def __init__(self,fname,xloc,yloc,projected=True,interval=10000.,xrange=[None, None],xscale=0.001):
        """Initialise.

        fname: name of CF file.
        xloc/yloc: control points along profile.
        projected: set to True (Default) if xloc/yloc are in projected coord system
        interval: linearly interpolate profile
        xrange: clip profile (Default [None,None])
        xscale: scale x values
        """
        
        CFloadfile.__init__(self,fname)

        # caching profiles
        self.__profiles = {}
        
        # vertical resoultion
        self.zres = 2.
        self.xscale = xscale
        
        if projected:
            self.xloc = xloc
            self.yloc = yloc
        else:
            self.xloc = []
            self.yloc = []
            for i in range(0,len(xloc)):
                point = self.project([xloc[i],yloc[i]])
                self.xloc.append(point[0])
                self.yloc.append(point[1])
                
        self.interval = interval
        self.interpolated = interpolate_xy([self.xloc,self.yloc],self.interval)

        if xrange[0] == None:
            start = 0
        else:
            start = int(xrange[0]/interval)
        if xrange[1] == None:
            end = len(self.interpolated[0,:])
        else:
            end = int(xrange[1]/interval+0.9999)
        self.interpolated = self.interpolated[:,start:end]
        self.xrange = [start*self.interval*xscale, end*self.interval*xscale]
        self.xvalues = []
        for i in range(0,len(self.interpolated[1,:])):
            self.xvalues.append(self.xrange[0]+i*self.interval*xscale)

        # clip to region of file
        interpx = []
        interpy = []
        xvalues = []
        for i in range(0,len(self.interpolated[1,:])):
            if self.inside_xy(self.interpolated[:,i]):
                interpx.append(self.interpolated[0,i])
                interpy.append(self.interpolated[1,i])
                xvalues.append(self.xvalues[i])
        self.xvalues = xvalues
        self.interpolated = Numeric.array([interpx,interpy],Numeric.Float32)

    def getprofile(self,var):
        """Get a profile variable from file.

        var: name of variables

        this method caches the return profile variable structure."""

        if var not in self.__profiles:
            self.__profiles[var] = CFprofile(self,var)
        return self.__profiles[var]

class CFprofile(CFvariable):
    """Handling CF Profiles."""

    def __init__(self,cfprofile,var):
        """Initialise.

        cfprofile: CF Profile file
        var: name of variable"""

        if not isinstance(cfprofile,CFloadprofile):
            raise ValueError, 'Not a profile file'

        CFvariable.__init__(cfprofile,var)

        #cache profile data
        self.__data = {}
        
    def getProfile(self,time,level=0):
        """Get a profile.

        time: time slice
        level: horizontal slice."""

        if time not in self.__data:
            self.__data[time] = {}
        if level not in self.__data[time]:
            var = self.getGMTgrid(time,level=level)
            self.__data[time][level] = var.grdtrack(self.interpolated[0,:],self.interpolated[1,:])

        return self.__data[time][level]
