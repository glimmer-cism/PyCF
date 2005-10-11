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
parser.profile_file()
parser.add_option("--land",action="store_true", dest="land",default=False,help="Indicate area above SL")
parser.add_option("--shapefile",metavar='FNAME',help="plot a shape file, e.g. LGM extent....")
parser.time()
parser.region()
parser.plot()
opts = PyCF.CFOptions(parser,-2)

dokey = opts.nfiles > 1

if opts.options.profname!=None:
    infile = opts.cfprofile()
else:
    infile = opts.cffile()
time = opts.times(infile)

# get number of plots
deltax = 1.
deltay = 1.
sizex = opts.options.width+deltax
sizey = infile.aspect_ratio*opts.options.width+deltay

plot = opts.plot()
bigarea = PyGMT.AreaXY(plot,size=opts.papersize)
area = PyCF.CFArea(bigarea,infile,pos=[0.,3.],size=sizex-deltax)
if opts.options.land:
    area.land(time)
area.coastline()

if dokey:
    key = PyGMT.KeyArea(bigarea,pos=[-2.,0.],size=[opts.options.width+4,2])
    key.num = [2,4]

for i in range(0,opts.nfiles):
    if opts.options.profname!=None:
        infile = opts.cfprofile(i)
    else:
        infile = opts.cffile(i)

    time = opts.times(infile)
    thk = infile.getvar('thk')
    area.contour(thk,[0.1],'-W2/%s'%PyCF.CFcolours[i],time)
    if dokey:
            key.plot_line(infile.title,'1/%s'%PyCF.CFcolours[i])
if opts.options.profname!=None:
    area.profile(args='-W5/0/0/0')
area.coordsystem()

if opts.options.shapefile != None:
    area.shapefile(opts.options.shapefile)


#if opts.options.dolegend:
#    PyGMT.colourkey(area,var.colourmap.cptfile,title=var.long_name,pos=[0,-2])
    
plot.close()
