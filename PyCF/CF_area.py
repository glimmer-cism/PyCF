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

"""Class for plotting ISM grid files."""

__all__ = ['CFArea']

import PyGMT,Numeric
from CF_loadfile import CFvariable

class CFArea(PyGMT.AreaXY):
    """CF grid plotting area."""

    def __init__(self,parent,cffile,pos=[0.,0.],size=10):
        """Initialising ISM area.

        parent: can be either a Canvas or another Area.
        cffile: CF file used for setting up projection and area
        pos: position of area relative to the parent
        size: size of GMT area
        """

        # initialising geographic area
        self.file = cffile
        if cffile.projection == 'lin':
            self.geo = PyGMT.AreaXY(parent,pos=pos,size=[size,cffile.aspect_ratio*size])
            self.geo.setregion([cffile.ll_geo[0]/cffile.deltax,cffile.ll_geo[1]/cffile.deltax],
                               [cffile.ur_geo[0]/cffile.deltax,cffile.ur_geo[1]/cffile.deltax])
        else:
            self.geo = PyGMT.AreaGEO(parent,cffile.projection.getGMTprojection(mapwidth=size).upper(), pos=pos, size=size)
            self.geo.setregion(cffile.ll_geo, cffile.ur_geo)
        # initialising paper area
        self.paper = PyGMT.AreaXY(parent,pos=pos,size=self.geo.size)

        # initialising XY area
        PyGMT.AreaXY.__init__(self,parent,pos=pos,size=self.geo.size)
        self.setregion(cffile.ll_xy, cffile.ur_xy)

    def coordsystem(self,grid=True):
        """Plot coordinate system.

        grid: if true plot lat/long grid"""
        self.geo.axis = self.axis
        self.geo.coordsystem(grid=grid)

    def coastline(self,args='-W -A0/1/1'):
        """Plot coastline.

        args: arguments passed on to pscoast."""
        try:
            self.geo.coastline(args)
        except:
            pass

    def stamp(self,text):
        """Print text in lower left corner."""

        self.paper.text([0.15,0.15],text,textargs='8 0 0 LB',comargs='-W255/255/255o')

    def printinfo(self,time):
        """Print a data name and time slice."""

        self.stamp('%s   %.2fka'%(self.file.title,self.file.time(time)))
        
    def image(self,var,time,level=0,clip=None):
        """Plot a colour map.

        var: CFvariable
        time: time slice
        level: horizontal slice
        clip: only display data where clip>0.
        """
        
        clipped = False
        if clip in ['topg','thk','usurf'] :
            cvar = CFvariable(var.cffile,clip)
            self.clip(cvar.getGMTgrid(time),0.1)
            clipped = True
        PyGMT.AreaXY.image(self,var.getGMTgrid(time,level=level),var.colourmap.cptfile)
        if clipped:
            self.unclip()

    def contour(self,var,contours,args,time,level=0):
        """Plot a contour map.

        var: CFvariable
        contours: list of contour intervals
        args: further arguments
        time: time slice
        level: horizontal slice."""

        PyGMT.AreaXY.contour(self,var.getGMTgrid(time,level=level),contours,args)

    def land(self,time,grey='240'):
        """Plot area above sea level.

        time: time slice
        grey: grey value."""

        cvar = CFvariable(self.file,'topg')
        self.clip(cvar.getGMTgrid(time),0.1)
        self.line('-W -L -G%s'%grey,[self.ll[0],self.ur[0],self.ur[0],self.ll[0]],[self.ll[1],self.ll[1],self.ur[1],self.ur[1]])
        self.unclip()

    def profile(self,args='-W1/0/0/0'):
        """Plot profile if present in file.

        args: pen arguments default -W1/0/0/0"""

        if hasattr(self.file,'interpolated'):
            self.line(args,self.file.interpolated[0,:].tolist(),self.file.interpolated[1,:].tolist())
    

if __name__ == '__main__':
    from CF_options import *

    parser = CFOptParser()
    parser.variable()
    parser.time()
    parser.region()
    parser.plot()

    opts = CFOptions(parser,2)
    infile = opts.cffile()
    var = opts.vars(infile)
    ts = opts.times(infile)
    plot = opts.plot()
    area = CFArea(plot,infile)
    if opts.options.land:
        area.land(ts)
    area.image(var,ts,clip = opts.options.clip)
    area.coastline()
    area.coordsystem()
    area.printinfo(ts)
    plot.close()
