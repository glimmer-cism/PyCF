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

"""Class for plotting time series."""

import PyGMT,Numeric

__all__ = ['CFAreaTS','CFEISforcing']

class CFAreaTS(PyGMT.AreaXY):
    """CF time series plotting area."""

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

    def newts(self):
        """Create a new time series plot."""

        newts = PyGMT.AutoXY(self.pt,pos=[self.ps[0],self.ps[1]+self.numplots*(self.size[1]+self.dy)],
                             size=self.size)
        self.plots.append(newts)
        self.numplots = self.numplots + 1
        return newts

    def finalise(self):
        """Finalise plot."""
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
                ts.finalise()
                if i==0:
                    ts.axis = 'WeSn'
                else:
                    ts.axis = 'Wesn'
                    ts.xlabel = ''
                i = i + 1
            self.totalarea = PyGMT.AreaXY(self.pt,pos=self.ps,
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

    def time(self,time,args='-W1/255/0/0'):
        """Draw a vertical line at time."""

        if not self.finalised:
            self.finalise()
        self.totalarea.line(args,[time,time],[0,1])

class CFEISforcing(CFAreaTS):
    """Plot EIS forcing functions."""

    def __init__(self,parent,pos=[0.,0.],size=[18.,5.]):
        """Initialising ISM area.

        parent: can be either a Canvas or another Area.
        pos: position of area relative to the parent
        size: size of GMT area
        """
        CFAreaTS. __init__(self,parent,pos=pos,size=size)

        self.timelab = 'time [ka]'
        self.slclab  = 'global average sea level [m]'
        self.templab = 'temperature [degC]'
        self.elalab  = 'Equilibrium line altitude variation [m]'
        
    def slc(self,times,slc):
        """Plot slc."""
        self.slc = self.newts()
        self.slc.add_line('-W1/0/0/0',times,slc)
        self.slc.xlabel = self.timelab
        self.slc.ylabel = self.slclab

    def temp(self,times,temp):
        """Plot temperature."""
        self.temp = self.newts()
        self.temp.add_steps('-W1/0/0/0',times,temp)
        self.temp.xlabel = self.timelab
        self.temp.ylabel = self.templab

    def ela(self,times,ela):
        """Plot elaerature."""
        self.ela = self.newts()
        self.ela.add_steps('-W1/0/0/0',times,ela)
        self.ela.xlabel = self.timelab
        self.ela.ylabel = self.elalab
    
if __name__ == '__main__':
    from CF_options import *
    from CF_IOmisc import *
    import sys

    parser = CFOptParser()
    parser.eisforcing()
    parser.time()
    parser.plot()

    opts = CFOptions(parser,1)
    plot = opts.plot()
    plot.defaults['LABEL_FONT_SIZE']='14p'
    plot.defaults['ANOT_FONT_SIZE']='12p'    
    area = CFEISforcing(plot)
    if opts.options.slcfile != None:
        try:
            slc = CFTimeSeries(opts.options.slcfile)
        except:
            print 'Cannot load SLC file %s'%opts.options.slcfile
            sys.exit(1)
        area.slc(slc.time,slc.data[:,0])
    if opts.options.tempfile != None:
        try:
            temp = CFEIStemp(opts.options.tempfile)
        except:
            print 'Cannot load temperature file %s'%opts.options.tempfile
            sys.exit(1)
        area.temp(temp.time,temp.data[:,0])
    if opts.options.elafile != None:
        try:
            ela = CFTimeSeries(opts.options.elafile)
        except:
            print 'Cannot load ELA file %s'%opts.options.elafile
            sys.exit(1)
        area.ela(ela.time,ela.data[:,0])    
    area.coordsystem()

    if opts.options.times!=None:
        for time in opts.options.times:
            area.time(time)
    
    plot.close()
