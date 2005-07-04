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
parser.region()
parser.plot()

opts = PyCF.CFOptions(parser,2)

infile = opts.cffile()
plot = opts.plot()

bigarea = PyGMT.AreaXY(plot,size=opts.papersize)
sizex=opts.options.width

key = PyGMT.KeyArea(bigarea,size=[sizex,2.])
key.num=[2,4]

area = PyCF.CFArea(bigarea,infile,pos=[0,3.],size=sizex)
area.land(0)
area.coastline()
rsl = PyCF.CFRSL(opts.options.rsldb)
area.rsl_locations(rsl,legend=key)
area.coordsystem()
plot.close()
