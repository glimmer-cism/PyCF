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

"plot stream locations"

import PyGMT,PyCF,sys, Numeric

# creating option parser
deltat = 1000.
parser = PyCF.CFOptParser()
parser.profile_file()
parser.time()
parser.add_option("--deltat",default=deltat,type="float",help="set integration interval (default %sa)"%deltat)
parser.region()
parser.plot()
opts = PyCF.CFOptions(parser,2)

if opts.options.profname!=None:
    infile = opts.cfprofile()
else:
    infile = opts.cffile()

deltat = opts.options.deltat*infile.timescale
time = opts.times(infile)
timeplus = infile.timeslice(infile.time(time)-deltat)

ubas = infile.getvar('ubas')
vbas = infile.getvar('vbas')

data = Numeric.zeros((len(ubas.xdim), len(ubas.ydim)),Numeric.Float32)

# loop over time slices
for t in range(timeplus,time+1):
    ugrid = ubas.get2Dfield(t)
    vgrid = vbas.get2Dfield(t)

    data = data + Numeric.where(ugrid!=0. or vgrid!=0, 1,0)
streams = ubas.getGMTgrid(time)
streams.data = data

# create a colour map
v0 = 0.1
v1 = max(Numeric.ravel(streams.data))
PyGMT.command('makecpt','-Cjet -T%f/%f/%f > .__auto.cpt'%(v0,v1,(v1-v0)/10.))
cpt = open('.__auto.cpt','a')
cpt.write('B       255     255     255\n')
cpt.close()

plot = opts.plot()
area = PyCF.CFArea(plot,infile,pos=[0.,3.])
PyGMT.AreaXY.image(area,streams,'.__auto.cpt')
thk = infile.getvar('thk')
area.contour(thk,[0.1],'-W2/0/0/0',time)
area.coastline()
area.coordsystem()
area.printinfo(time)
plot.close()
