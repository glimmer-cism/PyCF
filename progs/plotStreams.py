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

import PyGMT,PyCF,sys, Numeric, tempfile

# creating option parser
deltat = 1000.
parser = PyCF.CFOptParser()
parser.profile_file()
parser.time()
parser.add_option("--deltat",default=deltat,type="float",help="set integration interval (default %sa)"%deltat)
parser.add_option("--velocity",default=False,action="store_true",help="plot basal velocities integrated over time interval")
parser.var_options()
parser.region()
parser.plot()
opts = PyCF.CFOptions(parser,-2)

numplots = opts.nfiles

if opts.options.profname!=None:
    infile = opts.cfprofile()
else:
    infile = opts.cffile()

# get number of plots
deltax = 1.
deltay = 1.
sizex = opts.options.width+deltax
sizey = infile.aspect_ratio*opts.options.width+deltay

plot=None
numx = int((opts.papersize[0])/(sizex))
numy = int((opts.papersize[1])/(sizey))
numpages = int(float(numplots-0.1)/float(numx*numy))
p=-1

if opts.options.velocity:
    bvel = infile.getvar('bvel')
    colourmap = PyCF.CFcolourmap(bvel).cptfile
    ctitle = "average velocity [m/a]"
else:
    # create a colour map
    v0 = 0.1
    v1 = 1.
    cmapfile = tempfile.NamedTemporaryFile(suffix='.cpt')
    PyGMT.command('makecpt','-Cjet -T%f/%f/%f > %s'%(v0,v1,(v1-v0)/10.,cmapfile.name))
    cmapfile.seek(0,2)
    cmapfile.write('B       255     255     255\n')
    cmapfile.flush()    
    colourmap = cmapfile.name
    ctitle = "residency"

for i in range(0,numplots):
    if i%(numx*numy)==0:
        # need to open a new plot file
        if plot!=None:
            plot.close()
        if numpages>0:
            p=p+1
            plot = opts.plot(number=p)
        else:
            p=0
            plot = opts.plot()
        bigarea = PyGMT.AreaXY(plot,size=opts.papersize)
        if opts.options.dolegend:
            PyGMT.colourkey(bigarea,colourmap,args='-L',title=ctitle,pos=[0,opts.papersize[1]-(numy-1)*(sizey+deltay)])


    if opts.options.profname!=None:
        infile = opts.cfprofile(i)
    else:
        infile = opts.cffile(i)
        
    deltat = opts.options.deltat*infile.timescale
    time = opts.times(infile)
    time_start = infile.timeslice(infile.time(time)-0.5*deltat)
    time_end = infile.timeslice(infile.time(time)+0.5*deltat)

    bvel = infile.getvar('bvel')
    
    data = Numeric.zeros((len(bvel.xdim), len(bvel.ydim)),Numeric.Float32)

    # loop over time slices
    for t in range(time_start,time_end+1):
        vgrid = bvel.get2Dfield(t)

        if opts.options.velocity:
            data = data + vgrid
        else:
            data = data + Numeric.where(vgrid>0., 1,0)
    streams = bvel.getGMTgrid(time)
    streams.data = data/(time_end+1-time_start)
    
    x = i%numx
    y = int((i-p*(numx*numy))/numx)
    area = PyCF.CFArea(bigarea,infile,pos=[x*sizex,opts.papersize[1]-(y+1)*sizey],size=sizex-deltax)

    PyGMT.AreaXY.image(area,streams,colourmap)
    thk = infile.getvar('thk')
    area.contour(thk,[0.1],'-W2/0/0/0',time)
    area.coastline()
    if numplots>1:
        area.axis='wesn'
    area.coordsystem()
    area.printinfo(time)
        
plot.close()
