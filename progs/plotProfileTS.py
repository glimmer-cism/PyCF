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

"""A plot of CF profile timeseries."""

import PyGMT,PyCF,Numeric,sys

# creating option parser
parser = PyCF.CFOptParser()
parser.width=15.
parser.variable()
parser.profile_file()
parser.timeint()
parser.plot()
opts = PyCF.CFOptions(parser,2)
infile = opts.cfprofile()
try:
    t0 = opts.times(infile,0)
    t1 = opts.times(infile,1)
except:
    t0=0
    t1=infile.numt-1

if opts.options.level == None:
    level = 0
else:
    level = opts.options.level

profile = opts.profs(infile)
data = profile.getProfileTS(time=[t0,t1],level=level)

plot = opts.plot()
plot.defaults['LABEL_FONT_SIZE']='12p'
plot.defaults['ANOT_FONT_SIZE']='10p'

area = PyGMT.AreaXY(plot,size=opts.papersize)
area.setregion([0,infile.time(t0)],[infile.xvalues[-1],infile.time(t1)])
area.axis='WeSn'
area.xlabel = 'distance along profile'
area.ylabel = 'time'

clipped = False
clip = opts.options.clip
if clip in ['topg','thk','usurf'] :
    cvar = infile.getprofile(clip)
    cdata = cvar.getProfileTS(time=[t0,t1])
    area.clip(cdata,0.1)
    clipped = True
area.image(data,profile.colourmap.cptfile)
if clipped:
    area.unclip()



area.coordsystem()

plot.close()
