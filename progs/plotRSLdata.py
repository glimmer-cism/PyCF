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
parser.add_option("--ice_free",action="store_true",default=False,help='Only extract RSL for ice free areas')
parser.add_option("--id",default=1,metavar="ID",type="int",help="select RSL ID")
parser.add_option("--show_loc",action="store_true",default=False,help='Plot map showing location of RSL observation')
parser.time()
parser.region()
parser.plot()

opts = PyCF.CFOptions(parser,-1)

rsl = PyCF.CFRSL(opts.options.rsldb)

plot = opts.plot()
bigarea = PyGMT.AreaXY(plot,size=opts.papersize)

key = PyGMT.KeyArea(bigarea,size=[17,2.])
key.num=[3,4]

rslplot = PyCF.CFRSLArea(bigarea,rsl,opts.options.id,pos=[0.,3.5])
for i in range(0,opts.nfiles):
    infile = opts.cffile(i)
    try:
        rslplot.rsl_line(infile,pen='-W1/%s'%PyCF.CFcolours[i],clip=opts.options.ice_free)
        key.plot_line(infile.title,'1/%s'%PyCF.CFcolours[i])
    except:
        print 'Warning, cannot plot RSL line for file: %s'%infile.fname
        
    
rslplot.finalise(expandy=True)
rslplot.coordsystem()
rslplot.printinfo()

if opts.options.show_loc:
    loc = rsl.getLoc(opts.options.id)
    mapa = PyCF.CFArea(bigarea,infile,pos=[0,5.5+rslplot.size[1]],size=7.)
    mapa.coastline('-Dl -G170 -A0/1/1')
    mapa.geo.plotsymbol([loc[3]],[loc[4]],size=0.2,symbol='a',args='-G%s'%PyCF.CFcolours[loc[1]])
    mapa.coordsystem()
    mapakey = PyGMT.KeyArea(bigarea,size=[10.,2.],pos=[8.,5.5+rslplot.size[1]])
    mapakey.num=[1,1]
    ds = rsl.getDataset(loc[1])
    mapakey.plot_symbol(ds[1],PyCF.CFcolours[loc[1]],'a')
             

plot.close()


