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

"""Plot variable at single location."""

import PyGMT,PyCF,sys

# creating option parser
parser = PyCF.CFOptParser()
parser.spot()
parser.time()
parser.plot()
opts = PyCF.CFOptions(parser,2)
infile = opts.cffile()
var  = opts.vars(infile)

dotimes = True
time = None
if opts.ntimes == 1:
    time = opts.times(infile,0)
    dotimes = False
elif opts.ntimes>1:
    time = [opts.times(infile,0),opts.times(infile,1)]

dolevels = True
level = None
if opts.options.level != None:
    if len(opts.options.level) > 1:
        level = opts.options.level[0:1]
    elif len(opts.options.level) == 1:
        dolevels = False
        level = opts.options.level[0]
if 'level' not in var.var.dimensions:
    dolevels = False
    if level == None:
        level = 0

if not dolevels and not dotimes:
    dotimes = True
    time = None

plot = opts.plot()
plot.defaults['LABEL_FONT_SIZE']='12p'
plot.defaults['ANOT_FONT_SIZE']='10p'
bigarea = PyGMT.AreaXY(plot,size=opts.papersize)
area = PyGMT.AutoXY(bigarea,size=[opts.options.width,opts.options.width/2.])
key = PyGMT.KeyArea(bigarea,pos=[opts.options.width+1.,0.],size=[opts.options.width/2.,opts.options.width/2])
key.num = [1,10]
area.axis='WeSn'

i = 0
for ij in opts.options.ij:
    data = var.getSpotIJ(ij,time,level)
    if dotimes:
        area.add_line('-W1/%s'%PyCF.CFcolours[i],infile.time(time),data)
    elif dolevels:
        area.add_line('-W1/%s'%PyCF.CFcolours[i],data,infile.file.variables['level'])
    key.plot_line('(%d,%d)'%ij,'1/%s'%PyCF.CFcolours[i])
    i = i+1
        
if dotimes:
    area.xlabel = 'time'
    area.ylabel = '%s [%s]'%(var.long_name,var.units)
    area.finalise(expandy=True)
if dolevels:
    area.xlabel = '%s [%s]'%(var.long_name,var.units)
    area.ylabel = 'normalised height'
    area.finalise(expandx=True)
area.coordsystem()

plot.close()
