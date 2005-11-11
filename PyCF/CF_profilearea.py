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

__all__ = ['CFProfileArea','CFProfileMArea','CFProfileAreaTS']

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
        
        if profile.name == 'litho_temp':
            self.ylabel = 'depth [m]'
            
            data = profile.getProfile2D_litho(time)
            self.image(data,profile.colourmap.cptfile)
        elif profile.is3d and level == None and not profile.average:
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

class CFProfileAreaTS(PyGMT.AreaXY):
    """Plot time--distance diagram."""

    def __init__(self,parent,profile,time=None,clip=None,level=None,pos=[0.,0.],size=[18.,25.]):
        """Initialise.

        parent: can be either a Canvas or another Area.
        profile: CF profile
        var: name of variable to be plotted
        time: if None, return data for all time slices
              if list/etc of size two, interpret as array selection
        clip:
        level: level to be processed
        pos: position of area relative to the parent
        size: size of GMT area
        """

        self.mainarea = None
        self.upper_area = None
        self.lower_area = None
        self.epoch_area = None

        self.dy = 0.5
        self.dx = 0.
        self.finalised = False
        self.__main = {'clip':clip,'level':level}
        self.__profile = profile
        self.__profs = None
        self.__epoch = None
        self.__time = time

        self = PyGMT.AreaXY.__init__(self,parent,pos=pos,size=size)

    def plot_profs(self,var,height=4.):
        """Plot profiles above and below main area.

        var: name of variable to be plotted
        height: height of profile."""

        self.__profs = {'var':var,'height' : height}

    def plot_epoch(self,epoch,width=.6):
        """Plot epochs.

        epoch: epoch data
        widht: width of plot."""

        self.__epoch = {'epoch':epoch, 'width' :width}

    def finalise(self):
        """Finalise plot.

        i.e. set up region and do all the actual plotting."""

        if self.__epoch != None:
            width = self.size[0]-self.__epoch['width']-self.dx
        else:
            width = self.size[0]

        y = 0.
        
        if self.__profs != None:
            if self.__profs['var'] != None:
                profile = self.__profile.cffile.getprofile(self.__profs['var'])
            else:
                profile = self.__profile
            self.lower_area = CFProfileArea(self,profile,self.__time[0],size=[width,self.__profs['height']-self.dy],pos=[0.,0.])
            self.lower_area.finalise()

            self.upper_area = CFProfileArea(self,profile,self.__time[1],size=[width,self.__profs['height']-self.dy],pos=[0.,self.size[1]+self.dy-self.__profs['height']])
            self.upper_area.finalise()
            self.upper_area.axis='Wesn'

            height = self.size[1]-2*self.__profs['height']
            y = self.__profs['height']
            self.mainarea = PyGMT.AreaXY(self,size=[width,height],pos=[0.,y])
            self.mainarea.axis='Wesn'
        else:
            height = self.size[1]
            self.mainarea = PyGMT.AreaXY(self,size=[width,height],pos=[0.,0.])
            self.mainarea.axis='WeSn'
            self.mainarea.xlabel = 'distance along profile'

        self.mainarea.setregion([0,self.__profile.cffile.time(self.__time[0])],[self.__profile.cffile.xvalues[-1],self.__profile.cffile.time(self.__time[1])])
        self.mainarea.ylabel = 'time'

        data = self.__profile.getProfileTS(time=self.__time,level=self.__main['level'])

        clipped = False
        if self.__main['clip'] in ['topg','thk','usurf'] :
            cvar = self.__profile.cffile.getprofile(self.__main['clip'])
            cdata = cvar.getProfileTS(time=self.__time)
            self.mainarea.clip(cdata,0.1)
            clipped = True

        self.mainarea.image(data,self.__profile.colourmap.cptfile)
        if clipped:
            self.mainarea.unclip()

        if self.__main['clip'] != 'thk':
            cvar = self.__profile.cffile.getprofile('thk')
            cdata = cvar.getProfileTS(time=self.__time)
        self.mainarea.contour(cdata,[0.1],'-W1/0/0/0')

        if self.__epoch != None:
            self.epoch_area = PyGMT.AreaXY(self,size=[self.__epoch['width'],height],pos=[width,y])
            self.epoch_area.axis='wesn'
            self.epoch_area.setregion([0,self.__profile.cffile.time(self.__time[0])],[1,self.__profile.cffile.time(self.__time[1])])
            self.epoch_area.coordsystem()

           # plot boxes
            e = self.__epoch['epoch'].data
            for c in range(0,len(e)):
                t0 = e[c]['start']*self.__epoch['epoch'].timescale
                t1 = e[c]['end']*self.__epoch['epoch'].timescale
                x = [0.,1.,1.,0.]
                y = [t0,t0,t1,t1]
                self.epoch_area.line('-L -G%s -W1/0/0/0'%e[c]['colour'],x,y)
                self.epoch_area.text([0.5,(t0+t1)/2.],e[c]['name'],'10 90 0 CM')
                self.mainarea.line('-L -W1/0/0/0',[0.,self.__profile.cffile.xvalues[-1]],[t0,t0])
                self.mainarea.line('-L -W1/0/0/0',[0.,self.__profile.cffile.xvalues[-1]],[t1,t1])

        self.finalised = True

    def coordsystem(self):
        """Draw coordinate system."""

        if not self.finalised:
            self.finalise()

        if self.lower_area != None:
            self.lower_area.coordsystem()
        if self.upper_area != None:
            self.upper_area.coordsystem()
        if self.mainarea != None:
            self.mainarea.coordsystem()
