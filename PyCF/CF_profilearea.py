#! /usr/bin/env python

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

"""Class for plotting profiles extracted from CF files."""

__all__ = ['CFProfileArea','CFProfileMArea']

import PyGMT,Numeric

class CFProfileArea(PyGMT.AutoXY):
    """CF profile plotting area."""

    def __init__(self,parent,profile,time,level=None,pen='1/0/0/0',pos=[0.,0.],size=[18.,5.]):
        """Initialise.

        parent: can be either a Canvas or another Area.
        profile: CF profile
        time: time slice
        level: level to be processed
        pos: position of area relative to the parent
        size: size of GMT area
        """
        
        PyGMT.AutoXY.__init__(self,parent,pos=pos,size=size)
        self.file = profile.cffile
        self.axis='WeSn'
        self.xlabel = 'distance along profile [km]'
        self.plot(profile,time,level=level,pen=pen)
        self.__stamp = None

    def plot(self,profile,time,level=None,pen='1/0/0/0'):
        """Plot Profile.

        profile: CF profile
        time: time slice
        level: level to be processed"""
        
        if profile.is3d and level == None and not profile.average:
            self.ylabel = 'elevation [m]'

            data = profile.getProfile2D(time)
            self.image(data,profile.colourmap.cptfile)
            ihdata = Numeric.array(profile.cffile.getprofile('thk').getProfile(time))
            try:
                rhdata = Numeric.array(profile.cffile.getprofile('topg').getProfile(time))
                self.line('-W%s'%pen,profile.cffile.xvalues,rhdata)
            except:
                rhdata = Numeric.zeros(len(ihdata))
            ihdata = rhdata+ihdata
            self.line('-W%s'%pen,profile.cffile.xvalues,ihdata)
        else:
            if level == None:
                level = 0
            self.ylabel = '%s [%s]'%(profile.long_name,profile.units)
            data = profile.getProfile(time,level=level)
            self.line('-W%s'%pen,profile.cffile.xvalues,data)
            if profile.name == 'is':
                rhdata = Numeric.array(profile.cffile.getprofile('topg').getProfile(time))
                self.line('-W%s'%pen,profile.cffile.xvalues,rhdata)
            if profile.name in ['btemp','temp']:
                if not profile.pmt and profile.showpmp:
                    pmp = Numeric.array(profile.cffile.getprofile('pmp').getProfile(time))
                    self.line('-W%sta'%pen,profile.cffile.xvalues,pmp)
                
    def stamp(self,text):
        """Print text in lower left corner."""

        self.__stamp = text

    def printinfo(self,time=None):
        """Print a data name and time slice."""

        if time != None:
            self.stamp('%s   %.2fka'%(self.file.title,self.file.time(time)))
        else:
            self.stamp('%s'%(self.file.title))

    def finalise(self,expandx=False,expandy=False):
        """Finalise autoXY plot.

        i.e. set up region and do all the actual plotting.
        expandx, expandy: when set to True expand region to sensible value.
        """

        PyGMT.AutoXY.finalise(self,expandx=expandx,expandy=expandy)
        
        if self.__stamp != None:
            self.paper.text([self.paper.size[0]-0.15,self.paper.size[1]-0.15],
                            self.__stamp,textargs='8 0 0 RT',comargs='-W255/255/255o')
        
class CFProfileMArea(PyGMT.AreaXY):
    """Plot multiple profiles"""

    def __init__(self,parent,pos=[0.,0.],size=[18.,5.]):
        """Initialising ISM area.

        parent: can be either a Canvas or another Area.
        pos: position of area relative to the parent
        size: size of GMT area
        """

        self.numplots = 0
        self.pt = PyGMT.AreaXY(parent,pos=pos,size=[30.,30.])
        self.ps = pos
        self.size = size
        self.dy = 0.5
        self.finalised = False
        self.plots = []

    def newprof(self,profile,time,level=None,pen='1/0/0/0'):
        """Create a new profile plot.

        profile: CF profile
        time: time slice
        level: level to be processed"""

        newpr = CFProfileArea(self.pt,profile,time,level=level,pen=pen,pos=[0,self.numplots*(self.size[1]+self.dy)],
                              size=self.size)
        self.plots.append(newpr)
        self.numplots = self.numplots + 1
        return newpr

    def finalise(self,expandx=False,expandy=False):
        """Finalise plot.

        i.e. set up region and do all the actual plotting.
        expandx, expandy: when set to True expand region to sensible value."""
        if not self.finalised:
            if len(self.plots) == 0:
                raise RuntimeError, 'No plots added'
            # get global range of x values
            tsrange = [self.plots[0].ll[0], self.plots[0].ur[0]]
            for ts in self.plots:
                tsrange[0] = min(tsrange[0],ts.ll[0])
                tsrange[1] = max(tsrange[1],ts.ur[0])
            # finalise each plot
            i = 0
            for ts in self.plots:
                ts.ll[0] = tsrange[0]
                ts.ur[0] = tsrange[1]
                ts.finalise(expandx=expandx,expandy=expandy)
                if i==0:
                    ts.axis = 'WeSn'
                else:
                    ts.axis = 'Wesn'
                    ts.xlabel = ''
                i = i + 1
            self.totalarea = PyGMT.AreaXY(self.pt,
                                          size=[self.size[0],
                                                self.numplots * self.size[1] + (self.numplots-1) * self.dy])
            self.totalarea.setregion([ts.ll[0],0.],[ts.ur[0],1.])
            self.finalised=True

    def coordsystem(self,grid=False):
        """Draw coordinate system.

        grid: grid = anot if true and [xy]grid not set"""

        if not self.finalised:
            self.finalise()

        # loop over plots
        for ts in self.plots:
            ts.coordsystem(grid=grid)
