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

import PyGMT,PyCF,sys,math, Numeric


class plot_locations:
    def __init__(self,origin,size):
        x=size[0]/2.
        y=size[1]/2.
        t=math.pi/2.-math.atan2(y,x)
        self.a=x/math.cos(t)
        self.b=y/math.sin(t)
        self.x = origin[0]
        self.y = origin[1]

    def pos(self,a):
        x=self.x+self.a*math.cos(math.pi/2.-a)
        y=self.y+self.b*math.sin(math.pi/2.-a)
        return x,y

    def angle(self,i,num):
        a=2.*math.pi/num
        a=a/2.+i*a
        return a

    def center(self,i,num):
        a=self.angle(i,num)
        return self.pos(a)

    def con(self,i,num,size=[3.,2.]):
        (x,y) = self.center(i,num)
        a=self.angle(i,num)
        xs = size[0]/2.
        ys = size[1]/2.
        if a>0. and a<=math.pi/2.:
            return (x-xs,y-ys)
        elif a>math.pi/2. and a<=math.pi:
            return (x-xs,y+ys)
        elif a>math.pi and a<=3.*math.pi/2.:
            return (x+xs,y-ys)
        else:
            return (x+xs,y-ys)

    def loc(self,i,num,size=[3.,2.]):
        (x,y) = self.center(i,num)
        xs=size[0]/2.
        ys=size[1]/2.
        return (x-xs,y-ys)

xsize = 3.
ysize = 2.

# creating option parser
parser = PyCF.CFOptParser()
parser.width = 7.
parser.rsl()
parser.add_option("--ice_free",action="store_true",default=False,help='Only extract RSL for ice free areas')
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

# calculate position of plot
w = opts.options.width
h = infile.aspect_ratio*w
x = (plot.papersize[0]-w)/2.
y = (plot.papersize[1]-h)/2.
mapa_pos = [x-1.,y-1.]

mapa = PyCF.CFArea(bigarea,infile,pos=mapa_pos,size=opts.options.width)
mapa.axis='wesn'
mapa.coastline('-Dl -G170 -A0/1/1')
mapa.rsl_locations(rsl)
mapa.coordsystem()

plot_sites = PyCF.CFRSLlocs[opts.options.rsl_selection]
num_sites=len(plot_sites) #10
# calculate parameters of ellipse containing four corners of map
loc = []
con = []
ellipse = plot_locations([mapa_pos[0]+mapa.size[0]/2., mapa_pos[1]+mapa.size[1]/2],[mapa.size[0]+xsize+0.5, mapa.size[1]+ysize+.5])
key_y=mapa_pos[1]
for t in range(0,num_sites):
    pos = ellipse.con(t,num_sites,size=[xsize,ysize])
    con.append(list(pos))

    pos = ellipse.loc(t,num_sites,size=[xsize,ysize])
    loc.append(list(pos))
    key_y=min(key_y,pos[1])

key = PyGMT.KeyArea(bigarea,size=[17,3],pos=[0.,key_y-3.-ysize/2.])
key.num=[2,8]

# open netCDF files
cffile = []
for fnum in range(0,len(opts.args)-1):
    f = opts.cffile(fnum)
    if 'slc' in f.file.variables.keys():
        cffile.append(f)

# setup RSL plots
for i in range(0,len(plot_sites)):
    rslareas = PyCF.CFRSLArea(bigarea,rsl,plot_sites[i],pos=loc[i],size=[xsize,ysize])
    
    # plot RSL curves
    for fnum in range(0,len(cffile)):
        try:
            rslareas.rsl_line(cffile[fnum],pen='-W1/%s'%PyCF.CFcolours[fnum],clip=opts.options.ice_free)
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
    bigarea.line('-W',[con[i][0],rloc[0][0]+mapa_pos[0]],[con[i][1],rloc[1][0]+mapa_pos[1]])

# plot RSL curves
for fnum in range(0,len(cffile)):
    key.plot_line(cffile[fnum].title,'1/%s'%PyCF.CFcolours[fnum])
    
plot.close()
