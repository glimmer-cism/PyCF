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

import PyGMT,PyCF,Numeric,sys

# creating option parser
parser = PyCF.CFOptParser()
parser.width=15.
parser.profile()
parser.time()
parser.plot()
opts = PyCF.CFOptions(parser,-2)
infile = opts.cfprofile()

if opts.options.level == None:
    level = 0
else:
    level = opts.options.level

dokey = opts.nfiles > 1

plot = opts.plot()
plot.defaults['LABEL_FONT_SIZE']='12p'
plot.defaults['ANOT_FONT_SIZE']='10p'
bigarea = PyGMT.AreaXY(plot,size=opts.papersize)

if dokey:
    key = PyGMT.KeyArea(bigarea,pos=[-2.,0.],size=[opts.options.width+4,2])
    key.num = [2,4]
    key.plot_line(infile.title,'1/%s'%PyCF.CFcolours[0])

area = PyCF.CFProfileMArea(bigarea,pos=[0,3.5],size=[opts.options.width,opts.options.width/5.])
varea = []
for i in range(0,opts.nvars):
    profile = opts.profs(infile,i)
    time = opts.times(infile,0)
    varea.append(area.newprof(profile,time,level=opts.options.level,pen='1/%s'%PyCF.CFcolours[0]))

for f in range(1,opts.nfiles):
    infile = opts.cfprofile(f)
    for i in range(0,opts.nvars):
        profile = opts.profs(infile,i)
        time = opts.times(infile,0)
        varea[i].plot(profile,time,level=opts.options.level,pen='1/%s'%PyCF.CFcolours[f])
    if dokey:
        key.plot_line(infile.title,'1/%s'%PyCF.CFcolours[f])

area.finalise(expandy=True)
area.coordsystem()

plot.close()
