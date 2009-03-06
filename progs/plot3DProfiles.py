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

"""Plot multiple 3D profiles"""

import PyGMT,PyCF,Numeric,sys

# creating option parser
parser = PyCF.CFOptParser()
parser.width=15.
parser.profile()
parser.time()
parser.plot()
opts = PyCF.CFOptions(parser,-2)

plot = opts.plot()
plot.defaults['LABEL_FONT_SIZE']='12p'
plot.defaults['ANNOT_FONT_SIZE']='10p'
bigarea = PyGMT.AreaXY(plot,size=opts.papersize)

area = PyCF.CFProfileMArea(bigarea,pos=[0,1.5],size=[opts.options.width,opts.options.width/5.])
for i in range(0,opts.nfiles):
    infile = opts.cfprofile(i)
    profile = opts.profs(infile)
    time = opts.times(infile,0)
    prof_area = area.newprof(profile,time)
    prof_area.printinfo(time)

area.finalise(expandy=True)
area.coordsystem()
PyGMT.colourkey(bigarea,profile.colourmap.cptfile,title=profile.long_name,
                pos=[(opts.options.width-10)/2,-2.25],size=[10,0.5],args='-L')

plot.close()
