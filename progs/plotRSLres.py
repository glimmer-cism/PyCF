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

"""Plotting a RSL residuals"""

import PyGMT,PyCF,sys, Numeric, os.path

parser = PyCF.CFOptParser()
parser.add_option("--legend",action="store_true", dest="dolegend",default=False,help="Plot a colour legend")
parser.rsl()
parser.plot()

opts = PyCF.CFOptions(parser,2)

infile = opts.cffile()
p= infile.minmax_long
plot = opts.plot()
plot.defaults['LABEL_FONT_SIZE']='12p'
plot.defaults['ANOT_FONT_SIZE']='10p'

rsl = PyCF.CFRSL(opts.options.rsldb)
rsldata = infile.getRSLresiduals(rsl)

bigarea = PyGMT.AreaXY(plot,size=opts.papersize)

maparea = PyCF.CFArea(bigarea,infile,pos=[0.,4.],size=opts.options.width)
maparea.land(0)
cpt = maparea.rsl_res(rsl)
maparea.coastline()
maparea.coordsystem()
if opts.options.dolegend:
    PyGMT.colourkey(maparea,os.path.join(PyCF.CFdatadir,'rsl_res.cpt'),title='RSL residuals [meter]',args='-L',pos=[0,-2])

plot.close()
