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

"""Plotting difference between two CF files"""

__all__=['CFdiff']

import PyGMT,sys, Numeric
import Scientific.Statistics.Histogram
from CF_loadfile import CFchecklist
from CF_timeseries import CFAreaTS

class CFdiff(CFAreaTS):
    """Plot differences between two files."""

    def __init__(self,parent,cffile1,cffile2,time,pos=[0.,0.],size=[16.,3.]):
        """Initialising Area.

        parent: can be either a Canvas or another Area.
        cffile1: first CF file
        cffile2: second CF file
        time: if None, return data for all time slices
              if list/etc of size two, interpret as array selection
        pos: position of area relative to the parent
        size: size of GMT area
        """

        CFAreaTS.__init__(self,parent,pos=pos,size=size)
        self.cffile1 = cffile1
        self.cffile2 = cffile2
        self.time = time

    def newts(self):
        """Create a new diff plot."""

        newdiff = CFdiff_base(self.pt,self.cffile1,self.cffile2,self.time,pos=[0,self.numplots*(self.size[1]+self.dy)],
                             size=self.size)
        self.plots.append(newdiff)
        self.numplots = self.numplots + 1
        return newdiff

    def plothist(self,var,level=0,clip=None):
        """Plot a colourmap of the difference histogram.

        var: name of variable to be plotted
        level: horizontal slice
        clip: only display data where clip>0.
        """

        hist = self.newts()
        hist.plothist(var,level=level,clip=clip)

    def plotarea(self):
        """Plot difference between Ice Areas."""

        area = self.newts()
        area.plotarea()

    def plotvol(self):
        """Plot difference between Ice Volumes."""

        vol = self.newts()
        vol.plotvol()

    def plotmelt(self):
        """Plot difference between melt areas."""

        melt = self.newts()
        melt.plotmelt()

class CFdiff_base(PyGMT.AutoXY):
    """Base CFdiff class."""
    def __init__(self,parent,cffile1,cffile2,time,pos=[0.,0.],size=[16.,5.]):
        """Initialising Area.

        parent: can be either a Canvas or another Area.
        cffile1: first CF file
        cffile2: second CF file
        time: if None, return data for all time slices
              if list/etc of size two, interpret as array selection
        pos: position of area relative to the parent
        size: size of GMT area
        """

        self.cffile1 = cffile1
        self.cffile2 = cffile2

        # checking if we've got the same times
        (tarray,t1) = CFchecklist(time,self.cffile1.file.variables['time'])
        if not tarray:
            raise RuntimeError, 'time must be an array, etc.'
        try:
            self.cffile1.file.variables['time'][t1[0]:t1[1]] != self.cffile2.file.variables['time'][t1[0]:t1[1]]
        except:
            print self.cffile1.file.variables['time'][t1[0]:t1[1]]
            print self.cffile2.file.variables['time'][t1[0]:t1[1]]
            raise RuntimeError, 'time slices do not match'
        self.t1 = t1

        self.bins = 300
       
        PyGMT.AutoXY.__init__(self,parent,pos=pos,size=size)

        self.axis='WeSn'
        self.xlabel = 'Time'

    def plothist(self,var,level=0,clip=None):
        """Plot a colourmap of the difference histogram.

        var: name of variable to be plotted
        level: horizontal slice
        clip: only display data where clip>0.
        """

        fill = -1000000.
        v1 = self.cffile1.getvar(var)
        v2 = self.cffile2.getvar(var)
        if clip in ['topg','thk','usurf'] :
            cv1 = self.cffile1.getvar(clip)
            cv2 = self.cffile2.getvar(clip)
        else:
            cv1 = None
            cv2 = None

        self.ylabel = '%s [%s]'%(v1.long_name,v1.units)

        # find min and max differences
        maxv = -1000000.
        minv = 1000000.

        for t in range(0,self.t1[1]-self.t1[0]):
            diff = v1.get2Dfield(self.t1[0]+t,level=level) - v2.get2Dfield(self.t1[0]+t,level=level)
            if cv1 != None:
                cvar = cv1.get2Dfield(self.t1[0]+t,level=level) + cv2.get2Dfield(self.t1[0]+t,level=level)
                maxv = max(maxv, max(Numeric.ravel( Numeric.where(cvar > 0. , diff, -1000000.))))
                minv = min(minv, min(Numeric.ravel( Numeric.where(cvar > 0. , diff, 1000000.))))
            else:
                maxv = max(maxv, max(Numeric.ravel(diff)))
                minv = min(minv, min(Numeric.ravel(diff)))

        # get data
        hist_grid = Numeric.zeros([self.t1[1]-self.t1[0],self.bins],Numeric.Float)
        for t in range(0,self.t1[1]-self.t1[0]):
            diff = v1.get2Dfield(self.t1[0]+t,level=level) - v2.get2Dfield(self.t1[0]+t,level=level)
            if cv1 != None:
                cvar = cv1.get2Dfield(self.t1[0]+t,level=level) + cv2.get2Dfield(self.t1[0]+t,level=level)
                count = sum(Numeric.where(cvar > 0. , 1., 0.).flat)
                diff = Numeric.where(cvar > 0. , diff, -1000000.)
            else:
                count = diff.flat.shape[0]
            hist = Scientific.Statistics.Histogram.Histogram(Numeric.ravel(diff),self.bins,[minv,maxv])
            if count>0:
                hist_grid[t,:] = hist.array[:,1]/count

        # creating grid
        grid = PyGMT.Grid()
        grid.x_minmax = [self.cffile1.time(self.t1[0]),self.cffile1.time(self.t1[1])]
        grid.y_minmax = [minv,maxv]
        grid.data = Numeric.where(hist_grid>0.,hist_grid,-10)

        # creating a colourmap
        min_h = min(Numeric.ravel(hist_grid))
        max_h = max(Numeric.ravel(hist_grid))
        PyGMT.command('makecpt','-Crainbow -Z -T%f/%f/%f > .__auto.cpt'%(min_h,max_h,(max_h-min_h)/10.))
        f = open('.__auto.cpt','a')
        f.write('B       255     255     255')
        f.close()

        # plotting image
        PyGMT.AutoXY.image(self,grid,'.__auto.cpt')

        # and a colourkey
        cm = PyGMT.colourkey(self,'.__auto.cpt',pos=[self.size[0]+0.5,0],size=[.75,self.size[1]])

    def plotarea(self):
        """Plot difference between Ice Areas."""
        area1 = self.cffile1.getIceArea(time=self.t1)
        area2 = self.cffile2.getIceArea(time=self.t1)
        diff = Numeric.array(area1)-Numeric.array(area2)

        self.ylabel = 'ice area'

        PyGMT.AutoXY.line(self,'-W1/0/0/0',self.cffile1.time(self.t1),diff)

    def plotvol(self):
        """Plot difference between Ice Volumes."""
        vol1 = self.cffile1.getIceVolume(time=self.t1)
        vol2 = self.cffile2.getIceVolume(time=self.t1)
        diff = Numeric.array(vol1)-Numeric.array(vol2)

        self.ylabel = 'ice volume'

        PyGMT.AutoXY.line(self,'-W1/0/0/0',self.cffile1.time(self.t1),diff)

    def plotmelt(self):
        """Plot difference between melt areas."""
        melt1 = self.cffile1.getFracMelt(time=self.t1)
        melt2 = self.cffile2.getFracMelt(time=self.t1)
        diff = Numeric.array(melt1)-Numeric.array(melt2)

        self.ylabel = 'melt fraction'

        PyGMT.AutoXY.line(self,'-W1/0/0/0',self.cffile1.time(self.t1),diff)
