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

"""A plot of CF profile timeseries."""

import PyGMT,PyCF,numpy,sys

SIZE_Y = 4.

# creating option parser
parser = PyCF.CFOptParser()
parser.width=15.
parser.variable()
parser.add_option("--profvar",metavar='NAME',type="string",dest='profvar',help="plot variable NAME at beginning and end of time interval")
parser.epoch()
parser.profile_file()
parser.timeint()
parser.plot()
opts = PyCF.CFOptions(parser,2)
infile = opts.cfprofile()
profile = opts.profs(infile)
try:
    t0 = opts.times(infile,0)
    t1 = opts.times(infile,1)
except:
    t0=0
    t1=infile.numt-1

if opts.options.level == None:
    level = 0
else:
    level = opts.options.level

plot = opts.plot()
plot.defaults['LABEL_FONT_SIZE']='12p'
plot.defaults['ANNOT_FONT_SIZE']='10p'

area = PyCF.CFProfileAreaTS(plot,profile,time=[t0,t1],clip=opts.options.clip,level=level)
if opts.options.profvar != None:
    area.plot_profs(opts.options.profvar)
if opts.options.epoch != None:
    epoch = PyCF.CFEpoch(opts.options.epoch)
    area.plot_epoch(epoch)
area.coordsystem()

if opts.options.dolegend:
    PyGMT.colourkey(areats,profile.colourmap.cptfile,title=profile.long_name,args='-L',pos=[(opts.papersize[0]-10.)/2.,-2.8])

plot.close()

