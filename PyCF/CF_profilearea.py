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

__all__ = ['CFProfileArea']

import PyGMT,Numeric

class CFProfileArea(PyGMT.AutoXY):
    """CF profile plotting area."""

    def __init__(self,parent,profile,time,level=None,pos=[0.,0.],size=[18.,5.]):
        """Initialise.

        parent: can be either a Canvas or another Area.
        profile: CF profile
        time: time slice
        level: level to be processed
        pos: position of area relative to the parent
        size: size of GMT area
        """
        
        PyGMT.AutoXY.__init__(self,parent,pos=pos,size=size)
        self.axis='WeSn'
        self.xlabel = 'distance along profile [km]'
        if 'level' in profile.var.dimensions and level == None:
            self.ylabel = 'elevation [m]'

            data = profile.getProfile2D(time)
            self.image(data,profile.colourmap.cptfile)
            ihdata = Numeric.array(profile.cffile.getprofile('thk').getProfile(time))
            try:
                rhdata = Numeric.array(profile.cffile.getprofile('topg').getProfile(time))
                self.line('-W1/0/0/0',profile.cffile.xvalues,rhdata)
            except:
                rhdata = Numeric.zeros(len(ihdata))
            ihdata = rhdata+ihdata
            self.line('-W1/0/0/0',profile.cffile.xvalues,ihdata)
        else:
            if level == None:
                level = 0
            self.ylabel = '%s [%s]'%(profile.long_name,profile.units)
            data = profile.getProfile(time,level=level)
            self.line('-W1/0/0/0',profile.cffile.xvalues,data)

