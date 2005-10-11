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

__all__=['CFloadprofile','CFprofile']

import Numeric, PyGMT
from CF_loadfile import *
from CF_utils import CFinterpolate_xy
from PyGMT import Grid
from CF_utils import CFinterpolate_linear

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
        self.interpolated = CFinterpolate_xy([self.xloc,self.yloc],self.interval)

        if xrange[0] == None:
            start = 0
        else:
            start = int(xrange[0]/interval)
        if xrange[1] == None:
            end = len(self.interpolated[0,:])
        else:
            end = int(xrange[1]/interval+0.9999)
        self.interpolated = self.interpolated[:,start:end]
        self.interval = self.interval*xscale
        self.xrange = [start*self.interval, end*self.interval]
        self.xvalues = []
        for i in range(0,len(self.interpolated[1,:])):
            self.xvalues.append(self.xrange[0]+i*self.interval)

        # clip to region of file
        interpx = []
        interpy = []
        xvalues = []
        for i in range(0,len(self.interpolated[1,:])):
            if self.inside(self.interpolated[:,i]):
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

    def getExtent(self,time=None,interval=1):
        """Get ice extent along profile.

        time: if None, return data for all time slices
              if list/etc of size two, interpret as array selection
              if single value, get only this time slice

        interval: extract every interval timeslice      

        this is a hack, we start looking from the end of the profile and stop when we found
        a change from no ice to ice."""

        (tarray,t) = CFchecklist(time,self.file.variables['time'])
        values = []
        if tarray:
            for i in range(t[0],t[1]+1,interval):
                values.append(self.__getExtent(i))
            return values
        return self.__getExtent(t)

    def __getExtent(self,time):
        data = self.getprofile('thk').getProfile(time)
        #right BC
        if data[-1] > 0. and data[-1]<1.e10:
            return self.xvalues[-1]
        for i in range(len(data[:])-2,0,-1):
            if data[i] > 0. and data[i]<1.e10:
                return self.xvalues[i]
        # if we are at the end we just return position of last value to close data set
        return self.xvalues[0]

class CFprofile(CFvariable):
    """Handling CF Profiles."""

    def __init__(self,cfprofile,var):
        """Initialise.

        cfprofile: CF Profile file
        var: name of variable"""

        self.yres = 10.

        if not isinstance(cfprofile,CFloadprofile):
            raise ValueError, 'Not a profile file'

        CFvariable.__init__(self,cfprofile,var)
        self.showpmp = False

        #cache profile data
        self.__data = {}
        self.__data2d = {}
        
    def getProfile(self,time,level=0):
        """Get a profile.

        time: time slice
        level: horizontal slice."""

        #if time not in self.__data:
        #    self.__data[time] = {}
        #if level not in self.__data[time]:
        #    var = self.getGMTgrid(time,level=level)
        #    self.__data[time][level] = var.grdtrack(self.cffile.interpolated[0,:],self.cffile.interpolated[1,:])

        #return self.__data[time][level]
        var = self.getGMTgrid(time,level=level)
        return var.grdtrack(self.cffile.interpolated[0,:],self.cffile.interpolated[1,:])

    def getProfile2D_litho(self,time):
        """Get a 2D profile which is not in sigma coordsystem.

        i.e. litho temperature.

        time: time slice

        returns a GMT grid"""

        if 'lithoz' not in self.var.dimensions:
            raise ValueError, 'Not a 3D variable'


        ymin = self.file.variables['lithoz'][-1]
        ymax = self.file.variables['lithoz'][0]
        yres = 50.
        y = self.file.variables['lithoz'][:].tolist()
        y.reverse()

        # load data
        data = Numeric.zeros([len(self.file.variables['lithoz']), len(self.cffile.xvalues)], Numeric.Float32)
        for i in range(0,len(self.file.variables['lithoz'])):
            prof = self.getProfile(time,level=len(self.file.variables['lithoz'])-i-1)
            data[i,:] = prof

        # setup output grid
        grid = Grid()
        grid.x_minmax = [0,self.cffile.xvalues[-1]]
        grid.y_minmax = [ymin,ymax]
        numy=int((ymax-ymin)/yres)+1
        grid.data = Numeric.zeros([len(self.cffile.xvalues),numy], Numeric.Float32)

        # interpolate
        pos = (Numeric.arange(numy)-numy+1)*yres
        for j in range(0,len(self.cffile.xvalues)):
            interpolated = CFinterpolate_linear(y,data[:,j],pos)
            grid.data[j,:] = interpolated

        return grid

    def getProfile2D(self,time):
        """Get a 2D profile.

        time: time slice

        returns a GMT grid"""

        if 'level' not in self.var.dimensions:
            raise ValueError, 'Not a 3D variable'

        if time not in self.__data2d:
            # load ice thickness and bedrock profiles
            ihprof = Numeric.array(CFprofile(self.cffile,'thk').getProfile(time))
            try:
                rhprof = Numeric.array(CFprofile(self.cffile,'topg').getProfile(time))
            except:
                rhprof = Numeric.zeros(len(ihprof))
            ymin=min(rhprof)
            ymax=max(rhprof+ihprof)
            numy=int((ymax-ymin)/self.yres)+1

            # load data
            data = Numeric.zeros([len(self.file.variables['level']), len(self.cffile.xvalues)], Numeric.Float32)
            for i in range(0,len(self.file.variables['level'])):
                prof = self.getProfile(time,level=len(self.file.variables['level'])-i-1)
                data[i,:] = prof

            # setup output grid
            grid = Grid()
            grid.x_minmax = [0,self.cffile.xvalues[-1]]
            grid.y_minmax = [ymin,ymax]
            grid.data = Numeric.zeros([len(self.cffile.xvalues),numy], Numeric.Float32)
            grid.data[:,:] = -100000000.
            # interpolate
            rhprof = rhprof-ymin
            for j in range(0,len(self.cffile.xvalues)):
                if ihprof[j]>0.:
                    start = int(rhprof[j]/self.yres)
                    end   = int((rhprof[j]+ihprof[j])/self.yres)+1
                    pos = Numeric.arange(start*self.yres,end*self.yres,self.yres)
                    interpolated = CFinterpolate_linear(rhprof[j]+ihprof[j]*self.file.variables['level'][:],
                                                        data[:,j],
                                                        pos)
                    grid.data[j,start:end] = interpolated
            #self.__data2d[time] = grid
            return grid
        #return self.__data2d[time]

    def getProfileTS(self,time=None,level=0):
        """Get a time-distance data.

        
        time: if None, return data for all time slices
              if list/etc of size two, interpret as array selection
              if single value, get only this time slice
        level: horizontal slice."""

        (tarray,t) = CFchecklist(time,self.file.variables['time'])

        if tarray:
            data = []
            for i in range(t[0],t[1]+1):
                data.append(self.getProfile(i,level=level))
            grid = PyGMT.Grid()
            grid.x_minmax = [0,self.cffile.xvalues[-1]]
            grid.y_minmax = [self.cffile.time(t[0]),self.cffile.time(t[1])]
            grid.data = Numeric.transpose(Numeric.array(data))
            return grid
        else:
            return self.getProfile(t,level=level)
