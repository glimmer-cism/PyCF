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

"""A plot of CF profiles."""

import PyGMT,PyCF,sys

# creating option parser
parser = PyCF.CFOptParser()
parser.profile()
parser.time()
parser.plot()
opts = PyCF.CFOptions(parser,2)
infile = opts.cfprofile()


plot = opts.plot()
plot.defaults['LABEL_FONT_SIZE']='12p'
plot.defaults['ANOT_FONT_SIZE']='10p'
bigarea = PyGMT.AreaXY(plot,size=opts.papersize)

for i in range(0,opts.nvars):
    profile = opts.profs(infile,i)
    area = PyGMT.AutoXY(bigarea,size=[opts.options.width,opts.options.width/2.],pos=[1.,i*(opts.options.width/2.+0.5)])
    if i == 0:
        area.axis='WeSn'
        area.xlabel = 'distance along profile [km]'
    else:
        area.axis='Wesn'
        area.xlabel = ''
    area.ylabel = '%s [%s]'%(profile.long_name,profile.units)
    time = opts.times(infile,0)
    data = profile.getProfile(time)
    area.add_line('-W1/0/0/0',infile.xvalues,data)
    area.finalise(expandy=True)
    area.coordsystem()

plot.close()
