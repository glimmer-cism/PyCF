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

"""Plotting a RSL histogram"""

import PyGMT,PyCF,sys, Numeric

parser = PyCF.CFOptParser()
parser.timeint()
parser.rsl()
parser.add_option("--nohist1d",action="store_false", dest="hist1d",default=True,help="Don't plot the 1D histogram")
parser.add_option("--nohist2d",action="store_false", dest="hist2d",default=True,help="Don't plot the 2D histogram")
parser.add_option("--nolegend",action="store_false", dest="legend",default=True,help="Don't plot a colour legend")
parser.plot()

opts = PyCF.CFOptions(parser,2)

infile = opts.cffile()
p= infile.minmax_long
plot = opts.plot()

rsl = PyCF.CFRSL(opts.options.rsldb)
rsldata = infile.getRSLresiduals(rsl,time=opts.options.times)

area = PyCF.CFRSLAreaHistT(plot,rsldata,size=[opts.options.width,opts.options.width*2./3.])
area.plot_1dhist = opts.options.hist1d
area.plot_2dhist = opts.options.hist2d
area.plot_key = opts.options.legend
area.plot()
area.finalise()

plot.close()
