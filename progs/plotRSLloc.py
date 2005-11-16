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

"""Plotting RSL locations"""

import PyGMT,PyCF,sys

parser = PyCF.CFOptParser()
parser.rsl()
parser.add_option("--print_ids",default=False,action="store_true",help="print ids of RSL observations")
parser.region()
parser.plot()

opts = PyCF.CFOptions(parser,2)

infile = opts.cffile()
rsl = PyCF.CFRSL(opts.options.rsldb)
plot = opts.plot()

bigarea = PyGMT.AreaXY(plot,size=opts.papersize)
sizex=opts.options.width

data = []
id_dx = 3.75
id_dy = 0.25
if opts.options.print_ids:
    rsldata = rsl.getLocationRange(infile.minmax_long,infile.minmax_lat)
    
    idysize=opts.papersize[1]-14.
    idarea = PyGMT.AreaXY(bigarea,size=[opts.papersize[0],idysize],pos=[-2.,0.])
    for i in range(0,len(rsldata)):
        loc = rsldata[i]
        if infile.inside(infile.project([loc[3],loc[4]])):
            data.append("%d: (%.2fE %.2fN) %d"%(loc[0],loc[3],loc[4],loc[5]))

    ysize=(len(data)/5+1)*id_dy
    for i in range(0,len(data)):
        y = ysize-(i/5)*id_dy
        x = (i%5)*id_dx
        idarea.text([x,y],data[i],textargs='8 0 0 BL')


y=(len(data)/5)*id_dy
key = PyGMT.KeyArea(bigarea,size=[sizex,2.],pos=[-1,y+.5])
key.num=[2,4]

area = PyCF.CFArea(bigarea,infile,pos=[-1,y+3.5],size=sizex)
area.land(0)
area.coastline()
area.rsl_locations(rsl,legend=key)
area.coordsystem()

plot.close()
