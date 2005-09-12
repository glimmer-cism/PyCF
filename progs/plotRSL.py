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

"""Plotting RSL sea level curves"""

import PyGMT,PyCF,sys

xsize = 3.
ysize = 2.

# creating option parser
parser = PyCF.CFOptParser()
parser.rsl()
parser.timeint()
parser.region()
parser.plot()
opts = PyCF.CFOptions(parser,-2)

infile = opts.cffile()

rsl = PyCF.CFRSL(opts.options.rsldb)

plot = opts.plot()
plot.defaults['LABEL_FONT_SIZE']='12p'
plot.defaults['ANOT_FONT_SIZE']='10p'
bigarea = PyGMT.AreaXY(plot,size=opts.papersize)

mapa = PyCF.CFArea(bigarea,infile,pos=[4.,10.],size=7.)
mapa.axis='wesn'
mapa.coastline('-Dl -G170 -A0/1/1')
mapa.rsl_locations(rsl)
mapa.coordsystem()

key = PyGMT.KeyArea(bigarea,size=[17,6.])
key.num=[3,12]

plot_sites = PyCF.CFRSLlocs[opts.options.rsl_selection]

loc = [[7.5,17.5], [12,17], [12.5,13.5], [12.5,10.2], [11,7], [6,7], [1.5,8], [0,12], [1,15], [2.5,18]]
con = [[7.5,17.5], [12,17], [12.5,13.5], [12.5,10.2], [11,7+ysize], [6,7+ysize], [1.5,8+ysize], [0+xsize,12], [1+xsize,15], [2.5+xsize,18]]

# open netCDF files
cffile = []
for fnum in range(0,len(opts.args)-1):
    cffile.append(opts.cffile(fnum))

# setup RSL plots
for i in range(0,len(plot_sites)):
    rslareas = PyCF.CFRSLArea(bigarea,rsl,plot_sites[i],pos=loc[i],size=[xsize,ysize])
    
    # plot RSL curves
    for fnum in range(0,len(opts.args)-1):
        try:
            rslareas.rsl_line(cffile[fnum],pen='-W1/%s'%PyCF.CFcolours[fnum])
        except RuntimeError:
            print cffile[fnum].title,plot_sites[i]

    # finish plots
    rslareas.finalise(expandy=True)
    rslareas.coordsystem()
    rslareas.printinfo()
    del rslareas
    # connect plots
    rloc = rsl.getLoc(plot_sites[i])
    rloc =  mapa.geo.project([rloc[3]],[rloc[4]])
    bigarea.line('-W',[con[i][0],rloc[0][0]+4.],[con[i][1],rloc[1][0]+10.])

# plot RSL curves
for fnum in range(0,len(opts.args)-1):
    key.plot_line(cffile[fnum].title,'1/%s'%PyCF.CFcolours[fnum])
    
plot.close()
