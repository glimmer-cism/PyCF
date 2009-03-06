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

__all__ = ['CFRSLArea','CFRSLlocs','CFRSLAreaHist1D','CFRSLAreaHistT']

import PyGMT,Numeric, tempfile
from CF_IOrsl import *

CFRSLlocs = {'fenscan' : [74,70,103,105,95,214,219,107,89,77],
             'fenscan-full'      : [321,317,53,62,42,41,3,0,33,20],
             'britain' : [115, 120, 121, 124, 222, 125, 129, 123, 122, 137, 133, 116] }

class CFRSLArea(PyGMT.AutoXY):
    """CF RSL plotting area."""

    def __init__(self,parent,rsl,lid,time=[-20.,0.],pos=[0.,0.],size=[15.,10.]):
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
        if time==None:
            self.time = [-20.,0.]
        else:
            self.time = time
        self.errors = True
        self.symbolsize=0.1

    def rsl_line(self,cffile,pen='-W1/255/0/0',clip=False):
        """Plot RSL curve from CF file.

        cffile: CF file object
        pen: pen attributes for line."""

        t = [cffile.timeslice(self.time[0],round='d'),
             cffile.timeslice(self.time[1],round='u')]
        times = cffile.file.variables['time'][t[0]:t[1]+1]*self.timescale
        data = cffile.getRSL([self.location[3],self.location[4]],t,clip=clip)
        self.line(pen,times,data)

    def finalise(self,expandy=False):
        """Finalise autoXY plot.

        i.e. set up region and do all the actual plotting.
        expandy: when set to True expand region to sensible value.
        """

        data = self.rsl.getRSLobs(self.lid)
        for obs in data:
            if self.errors:
                self.point([obs[2]*self.timescale],[obs[3]],[obs[5]*self.timescale],[obs[7]])
            self.plotsymbol([obs[2]*self.timescale],[obs[3]],size=self.symbolsize)

        self.ll[0] = self.time[0]
        self.ur[0] = self.time[1]
        PyGMT.AutoXY.finalise(self,expandy=expandy)

    def printinfo(self):
        """Print location name"""

        loc = self.rsl.getLoc(self.lid)
        infoarea = PyGMT.AreaXY(self,pos=[0.,self.size[1]],size=[self.size[0],0.5])
        infoarea.text([self.size[0]/2.,0.25],loc[2],textargs='8 0 0 CM')

class CFRSLAreaHist1D(PyGMT.AutoXY):
    """Plot a 1D histogram of RSL residuals."""
    def __init__(self,parent,rsldata,pos=[0.,0.], size=[15.,10.]):
        """Initialise.

        parent: can be either a Canvas or another Area.
        rsldata: rsl residual histogram data
        pos: position of area relative to the parent
        size: size of GMT area
        """

        PyGMT.AutoXY.__init__(self,parent,pos=pos,size=size)
        self.__rsldata = rsldata
        self.axis='WSen'
        self.xlabel = 'residuals [m]'
        self.ylabel = 'count'

    def plot(self,colourmap=None):
        """Plot RSL residuals.

        colourmap: if not None, use colourmap to indicate residuals"""

        counts = Numeric.sum(self.__rsldata.data,0)
        dx = (self.__rsldata.y_minmax[1]-self.__rsldata.y_minmax[0])/(len(counts)-1)
        bins = Numeric.arange(self.__rsldata.y_minmax[0],self.__rsldata.y_minmax[1]+dx,dx)
        if colourmap==None:
            self.steps('-W1',bins,counts)
        else:
            for i in range(0,min(len(counts),len(bins))):
                self.plotsymbol([bins[i]],[counts[i]],size="%f %f"%(float(bins[i]),dx),symbol="b%fu"%dx,args="-W1 -C%s"%colourmap)

class CFRSLAreaHistT(PyGMT.AreaXY):
    """Plot 2D histogram of RSL time-residuals."""

    def __init__(self,parent,rsldata,pos=[0.,0.],size=[15.,10.]):
        """Initialise.

        parent: can be either a Canvas or another Area.
        rsldata: rsl residual histogram data
        pos: position of area relative to the parent
        size: size of GMT area
        """

        PyGMT.AreaXY.__init__(self,parent,pos=pos,size=size)
        self.__rsldata = rsldata
        self.__cmap = None

        self.__plot_2dhist = True
        self.__plot_1dhist = True
        self.__plot_key = True
        self.defaults['LABEL_FONT_SIZE']='12p'
        self.defaults['ANNOT_FONT_SIZE']='10p'

    def __get_2dhist(self):
        return self.__plot_2dhist
    def __set_2dhist(self,value):
        self.__plot_2dhist = bool(value)
        self.__plot_key = self.__plot_2dhist
    plot_2dhist = property(__get_2dhist,__set_2dhist)

    def __get_1dhist(self):
        return self.__plot_1dhist
    def __set_1dhist(self,value):
        self.__plot_1dhist = bool(value)
    plot_1dhist = property(__get_1dhist,__set_1dhist)
    
    def __get_key(self):
        if self.__plot_2dhist:
            return self.__plot_key
        else:
            return False
    def __set_key(self,value):
        self.__plot_key = bool(value)
    plot_key = property(__get_key,__set_key)

    def setcolourmap(self,vmin=None,vmax=None):
        """Set colourmap for residual plot.

        vmin: minimum value
        vmax: maximum value"""

        if vmin==None:
            v0 = 1
        else:
            v0 = vmin
        if vmax==None:
            v1 = max(Numeric.ravel((self.__rsldata.data)))
        else:
            v1 = vmax

        self.__cmap = tempfile.NamedTemporaryFile(suffix='cpt')
        PyGMT.command('makecpt','-Ccool -T%f/%f/%f -Z > %s'%(v0,v1,(v1-v0),self.__cmap.name))
        self.__cmap.seek(0,2)
        self.__cmap.write('B       255     255     255\n')
        self.__cmap.flush()
            
    def plot(self):
        """Plot RSL histogram."""

        if self.__cmap==None:
            self.setcolourmap()

        self.area2d = None
        self.area1d = None

        y = 0.
        if self.plot_key:
            PyGMT.colourkey(self,self.__cmap.name,pos=[self.size[0]/8.,0.],size=[3.*self.size[0]/4.,.5])
            y = 2.

        if self.plot_2dhist and self.__plot_1dhist:
            self.area2d = PyGMT.AutoXY(self,pos=[0.,y],size=[3.*self.size[0]/4.,self.size[1]-y])
            self.area1d = PyGMT.AutoXY(self,pos=[3.*self.size[0]/4.,y],size=[self.size[0]/4.,self.size[1]-y])
        else:
            if self.plot_2dhist:
                self.area2d = PyGMT.AutoXY(self,pos=[0.,y],size=[self.size[0],self.size[1]-y])
            if self.plot_1dhist:
                self.area1d = PyGMT.AutoXY(self,pos=[0.,y],size=[self.size[0],self.size[1]-y])

        if self.plot_2dhist:
            self.area2d.axis='WSen'
            self.area2d.xlabel = 'time [ka]'
            self.area2d.ylabel = 'residuals [m]'
            self.area2d.image(self.__rsldata,self.__cmap.name)

        if self.plot_1dhist:
            counts = Numeric.sum(self.__rsldata.data,0)
            dx = (self.__rsldata.y_minmax[1]-self.__rsldata.y_minmax[0])/(len(counts)-1)
            bins = Numeric.arange(self.__rsldata.y_minmax[0],self.__rsldata.y_minmax[1]+dx,dx)

            if self.plot_2dhist:
                self.area1d.steps('-W1',counts,bins)
                self.area1d.ur[0] = PyGMT.round_up(self.area1d.ur[0])
                self.area1d.xlabel = 'count'
                self.area1d.axis='wSen'
            else:
                self.area1d.steps('-W1',bins,counts)
                self.area1d.ur[1] = PyGMT.round_up(self.area1d.ur[1])
                self.area1d.xlabel = 'residuals [m]'
                self.area1d.ylabel = 'count'
                self.area1d.axis='WSen'

    def finalise(self):
        """Finalise plots."""

        if self.plot_1dhist:
            self.area1d.finalise()
            self.area1d.coordsystem()
        if self.plot_2dhist:
            self.area2d.finalise()
            self.area2d.coordsystem()


if __name__ == '__main__':
    from CF_options import *
    from CF_IOrsl import *
    
    parser = CFOptParser()
    parser.rsl()
    parser.add_option("--id",default=1,metavar="ID",type="int",help="select RSL ID")
    parser.time()
    parser.region()
    parser.plot()

    opts = CFOptions(parser,1)
    #infile = opts.cffile()
    plot = opts.plot()

    rsl = CFRSL(opts.options.rsldb)

    rslplot = CFRSLArea(plot,rsl,opts.options.id)
    rslplot.finalise(expandx=True,expandy=True)
    rslplot.coordsystem()
    rslplot.printinfo()

    plot.close()
