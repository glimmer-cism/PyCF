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

SIZE_Y = 4.

# creating option parser
parser = PyCF.CFOptParser()
parser.width=15.
parser.variable()
parser.add_option("--profvar",metavar='NAME',type="string",dest='profvar',help="plot variable NAME at beginning and end of time interval")
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

plot = opts.plot()
plot.defaults['LABEL_FONT_SIZE']='12p'
plot.defaults['ANOT_FONT_SIZE']='10p'

bigarea = PyGMT.AreaXY(plot,size=opts.papersize)

if opts.options.profvar != None:
    areats = PyGMT.AreaXY(bigarea,size=[opts.papersize[0],opts.papersize[1]-2*SIZE_Y],pos=[0.,SIZE_Y])
    areats.axis='Wesn'

    profile = infile.getprofile(opts.options.profvar)
    area1 = PyCF.CFProfileArea(bigarea,profile,t0,size=[opts.papersize[0],SIZE_Y-.5])
    area1.finalise()
    area1.coordsystem()
    area2 = PyCF.CFProfileArea(bigarea,profile,t1,pos=[0.,opts.papersize[1]-SIZE_Y+0.5],size=[opts.papersize[0],SIZE_Y-0.5])
    area2.axis='Wesn'
    area2.finalise()
    area2.coordsystem()
else:
    areats = PyGMT.AreaXY(bigarea,size=opts.papersize)
    areats.axis='WeSn'
    areats.xlabel = 'distance along profile'

areats.setregion([0,infile.time(t0)],[infile.xvalues[-1],infile.time(t1)])
areats.ylabel = 'time'

profile = opts.profs(infile)
data = profile.getProfileTS(time=[t0,t1],level=level)



clipped = False
clip = opts.options.clip
if clip in ['topg','thk','usurf'] :
    cvar = infile.getprofile(clip)
    cdata = cvar.getProfileTS(time=[t0,t1])
    areats.clip(cdata,0.1)
    clipped = True
areats.image(data,profile.colourmap.cptfile)
if clipped:
    areats.unclip()

areats.coordsystem()

plot.close()
