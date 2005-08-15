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
parser.region1d()
parser.plot()
opts = PyCF.CFOptions(parser,-2)

mfiles = opts.nfiles>1
mspots = len(opts.options.ij)>1

plot = opts.plot()
plot.defaults['LABEL_FONT_SIZE']='12p'
plot.defaults['ANOT_FONT_SIZE']='10p'
bigarea = PyGMT.AreaXY(plot,size=opts.papersize)
if mspots and mfiles:
    multi_area = PyCF.CFAreaTS(bigarea,pos=[0,3.5],size=[opts.options.width,opts.options.width/2.])
    marea = []
    for i in range(0,len(opts.options.ij)):
        marea.append(multi_area.newts())
    key = PyGMT.KeyArea(bigarea,pos=[-2.,0.],size=[opts.options.width+4,2])
    key.num = [2,4]    
else:
    area = PyGMT.AutoXY(bigarea,size=[opts.options.width,opts.options.width/2.])
    area.axis='WeSn'
    key = PyGMT.KeyArea(bigarea,pos=[opts.options.width+1.,0.],size=[opts.options.width/2.,opts.options.width/2])
    key.num = [1,10]


for f in range(0,opts.nfiles):
    infile = opts.cffile(f)
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
    if 'level' not in var.var.dimensions and 'lithoz' not in var.var.dimensions:
        dolevels = False
        if level == None:
            level = 0

    if not dolevels and not dotimes:
        dotimes = True
        time = None

    if dolevels:
        if 'level' in var.var.dimensions:
            ldata = infile.file.variables['level']
            lname = infile.file.variables['level'].long_name
        elif 'lithoz' in var.var.dimensions:
            ldata = infile.file.variables['lithoz']
            lname = infile.file.variables['lithoz'].long_name

    i = 0
    colour=0
    for ij in opts.options.ij:
        if mspots and mfiles:
            area = marea[i]
            colour = f
        elif mspots:
            colour = i
        elif mfiles:
            colour = f
        data = var.getSpotIJ(ij,time,level)
        if dotimes:
            area.line('-W1/%s'%PyCF.CFcolours[colour],infile.time(time),data)
        elif dolevels:
            if mfiles and mspots:
                area.line('-W1/%s'%PyCF.CFcolours[colour],ldata,data)
            else:
                area.line('-W1/%s'%PyCF.CFcolours[colour],data,ldata)
        if mfiles and mspots:
            if i == 0:
                key.plot_line(infile.title,'1/%s'%PyCF.CFcolours[colour])  
        elif mfiles:
            key.plot_line(infile.title,'1/%s'%PyCF.CFcolours[colour])
        else:
            key.plot_line('(%d,%d)'%ij,'1/%s'%PyCF.CFcolours[colour])
        i = i+1

if mspots and mfiles:
    i = 0
    for ij in opts.options.ij:
        if dotimes:
            marea[i].xlabel = 'time'
            marea[i].ylabel = '%s [%s] (%d,%d)'%(var.long_name,var.units,ij[0],ij[1])
        if dolevels:
            marea[i].ylabel = '%s [%s] (%d,%d)'%(var.long_name,var.units,ij[0],ij[1])
            marea[i].xlabel = 'normalised height'
        i = i + 1
    multi_area.finalise(expandy=True)
    multi_area.coordsystem()
else:
    expandx = None
    expandy = None
    if opts.options.noxauto==True:
        expandx = False
    if opts.options.noyauto==True:
        expandy = False
    if opts.options.xrange != None:
        expandx = False
        area.ll[0] = opts.options.xrange[0]
        area.ur[0] = opts.options.xrange[1]
    if opts.options.yrange != None:
        expandy = False
        area.ll[1] = opts.options.yrange[0]
        area.ur[1] = opts.options.yrange[1]

    if dotimes:
        if expandx == None:
            expandx = False
        if expandy == None:
            expandy = True
        area.xlabel = 'time'
        area.ylabel = '%s [%s]'%(var.long_name,var.units)
        area.finalise(expandx=expandx,expandy=expandy)
    if dolevels:
        if expandx == None:
            expandx = True
        if expandy == None:
            expandy = False
        area.xlabel = '%s [%s]'%(var.long_name,var.units)
        area.ylabel = lname
        area.finalise(expandx=expandx,expandy=expandy)
    area.coordsystem()

plot.close()
