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

"""Plotting RSL data."""

__all__ = ['CFRSLArea','CFRSLlocs']

import PyGMT,Numeric
from CF_IOrsl import *

CFRSLlocs = {'fenscan' : [74,70,103,105,95,214,219,107,89,77]}

class CFRSLArea(PyGMT.AutoXY):
    """CF RSL plotting area."""

    def __init__(self,parent,rsl,lid,time=[-20000.,0.],pos=[0.,0.],size=[15.,10.]):
        """Initialising GMT area.

        parent: can be either a Canvas or another Area.
        rsl: rsl data base
        lid: location id to be plotted
        time: time interval to be processed (default [-20000.,0.])
        pos: position of area relative to the parent
        size: size of GMT area
        """

        PyGMT.AutoXY.__init__(self,parent,pos=pos,size=size)

        self.rsl = rsl
        self.lid = lid
        self.location = self.rsl.getLoc(self.lid)
        self.axis='WS'
        self.timescale = 0.001
        self.time = time

    def rsl_line(self,cffile,pen='-W1/255/0/0'):
        """Plot RSL curve from CF file.

        cffile: CF file object
        pen: pen attributes for line."""

        t = [cffile.timeslice(self.time[0]*cffile.timescale,round='d'),
             cffile.timeslice(self.time[1]*cffile.timescale,round='u')]
        times = cffile.file.variables['time'][t[0]:t[1]+1]*self.timescale
        data = cffile.getRSL([self.location[3],self.location[4]],t)
        self.line(pen,times,data)

    def finalise(self,expandy=False):
        """Finalise autoXY plot.

        i.e. set up region and do all the actual plotting.
        expandy: when set to True expand region to sensible value.
        """

        data = self.rsl.getRSLobs(self.lid)
        for obs in data:
            self.point([obs[2]*self.timescale],[obs[3]],[obs[5]*self.timescale],[obs[7]])

        self.ll[0] = self.time[0]*self.timescale
        self.ur[0] = self.time[1]*self.timescale
        PyGMT.AutoXY.finalise(self,expandy=expandy)

    def printinfo(self):
        """Print location name"""

        loc = self.rsl.getLoc(self.lid)
        infoarea = PyGMT.AreaXY(self,pos=[0.,self.size[1]],size=[self.size[0],0.5])
        infoarea.text([self.size[0]/2.,0.25],loc[2],textargs='8 0 0 CM')

if __name__ == '__main__':
    from CF_options import *
    from CF_IOrsl import *
    
    parser = CFOptParser()
    parser.time()
    parser.region()
    parser.plot()

    opts = CFOptions(parser,1)
    #infile = opts.cffile()
    plot = opts.plot()

    rsl = CFRSL('/home/magi/Development/src/PyCF/pelt.dat')

    rslplot = CFRSLArea(plot,rsl,1)
    rslplot.finalise(expandx=True,expandy=True)
    rslplot.coordsystem()
    rslplot.printinfo()

    plot.close()
