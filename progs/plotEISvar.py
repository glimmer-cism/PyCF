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

"""A simple plot of CF fields."""

import PyGMT,PyCF,sys

# creating option parser
parser = PyCF.CFOptParser()
parser.variable()
parser.time()
parser.region()
parser.eisforcing()
parser.plot()
opts = PyCF.CFOptions(parser,2)
infile = opts.cffile()

if opts.ntimes>1 or opts.nvars>1:
    sys.stderr.write('Error, can only handle a single time slice and variable')
    sys.exit(1)

numforce = 0
force=[10.,2.5]
dforce = 0.5
if opts.options.slcfile != None:
    numforce = numforce + 1
    try:
        slc = PyCF.CFTimeSeries(opts.options.slcfile)
    except:
        print 'Cannot load SLC file %s'%opts.options.slcfile
        sys.exit(1)
if opts.options.tempfile != None:
    numforce = numforce + 1
    try:
        temp = PyCF.CFEIStemp(opts.options.tempfile)
    except:
        print 'Cannot load temperature file %s'%opts.options.tempfile
        sys.exit(1)
if opts.options.elafile != None:
    numforce = numforce + 1
    try:
        ela = PyCF.CFTimeSeries(opts.options.elafile)
    except:
        print 'Cannot load ELA file %s'%opts.options.elafile
        sys.exit(1)

starty = numforce*force[1]+(numforce-1)*dforce
if starty>0.:
    starty = starty+2.

# get number of plots
deltax = 1.
deltay = 1.
sizex = opts.options.width+deltax
sizey = infile.aspect_ratio*opts.options.width+deltay

plot=None
var  = opts.vars(infile)
time = opts.times(infile)

plot = opts.plot()
plot.defaults['LABEL_FONT_SIZE']='12p'
bigarea = PyGMT.AreaXY(plot,size=opts.papersize)
area = PyCF.CFArea(bigarea,infile,pos=[0,starty],size=sizex-deltax)
if opts.options.land:
    area.land(time)
area.image(var,time,clip = opts.options.clip)
area.coastline()
area.coordsystem()
area.printinfo(time)

if starty>0.:            
    area = PyCF.CFEISforcing(bigarea,pos=[.5,0.],size=force)
if opts.options.slcfile != None:
    area.slc(slc.time,slc.data[:,0])
if opts.options.tempfile != None:
    area.temp(temp.time,temp.data[:,0])
if opts.options.elafile != None:
    area.ela(ela.time,ela.data[:,0])    
if starty>0.:
    area.coordsystem()
    area.time(opts.options.times[0])

    
plot.close()
