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

"""A simple plot of CF fields."""

import PyGMT,PyCF,sys,string

def parse_time(infile,opts):
    time = None
    times = []
    annotated_times = []
    if opts.options.times != None:
        tstring = opts.options.times.split('/')
        if len(tstring)==1:
            time = infile.timeslice(float(opts.options.times))
        elif len(tstring)>2 and len(tstring)<5:
            ts = infile.timeslice(float(tstring[0]),round='d')
            te = infile.timeslice(float(tstring[1]),round='u')
            dt = infile.timeslice(float(tstring[0])+float(tstring[2]),round='u')-ts
            if len(tstring) == 4:
                da = infile.timeslice(float(tstring[0])+float(tstring[3]),round='u')-ts
            else:
                da = None    
    else:
        tstring = opts.options.timeslice.split('/')
        if len(tstring)==1:
            time = int(opts.options.timeslice)
        elif len(tstring)>2 and len(tstring)<5:
            ts = int(tstring[0])
            te = int(tstring[1])
            dt = int(tstring[2])
            if len(tstring) == 4:
                da = int(tstring[3])
            else:
                da = None
        else:
            parser.error('Cannot parse timeslice string %s'%opts.options.timeslice)
    if time == None:
        times = range(ts,te,dt)
        if da!=None:
            annotated_times = range(ts,te,da)
    return (time,times,annotated_times)
    


# creating option parser
parser = PyCF.CFOptParser()
parser.profile_file(plist=True)
parser.add_option("--land",action="store_true", dest="land",default=False,help="Indicate area above SL")
parser.add_option("--shapefile",metavar='FNAME',help="plot a shape file, e.g. LGM extent....")
parser.add_option("-t","--time",metavar='TIME',dest="times",help="either time to be processed, or TIME=start/end/interval[/annotated interval]")
parser.add_option("-T","--timeslice",metavar='TIME',dest="timeslice",help="either time slice to be processed, or TIME=start/end/interval[/annotated interval]")
parser.region()
parser.plot()
opts = PyCF.CFOptions(parser,-2)

dokey = opts.nfiles > 1

infile = opts.cffile()

# setup times
(time,times,annotated_times) = parse_time(infile,opts)
# get number of plots
deltax = 1.
deltay = 1.
sizex = opts.options.width+deltax
sizey = infile.aspect_ratio*opts.options.width+deltay

plot = opts.plot()
bigarea = PyGMT.AreaXY(plot,size=opts.papersize)
area = PyCF.CFArea(bigarea,infile,pos=[0.,3.],size=sizex-deltax)
if opts.options.land:
    area.land(time)
area.coastline()

if dokey:
    key = PyGMT.KeyArea(bigarea,pos=[-2.,0.],size=[opts.options.width+4,2])
    key.num = [2,4]

for i in range(0,opts.nfiles):
    infile = opts.cffile(i)
    (time,times,annotated_times) = parse_time(infile,opts)
    if time != None:
        area.extent('-W2/%s'%PyCF.CFcolours[i],time,cffile=infile)
    else:
        for t in times:
            if t not in annotated_times:
                area.extent('-W2/%s'%PyCF.CFcolours[i],t,cffile=infile)
        for t in annotated_times:
            area.extent('-W2/%s'%PyCF.CFcolours[i],t,cffile=infile,cntrtype='a')
    if dokey:
            key.plot_line(infile.title,'1/%s'%PyCF.CFcolours[i])

if opts.options.profname!=None:
    i = 0
    for pn in opts.options.profname:
        pdata = PyCF.CFprofile(infile,interval=opts.options.interval)
        pdata.coords_file(pn,opts.options.prof_is_projected)
        area.profile(args='-W5/0/0/0',prof=pdata,slabel=string.ascii_uppercase[i])
        i=i+1
            
area.coordsystem()

if opts.options.shapefile != None:
    area.shapefile(opts.options.shapefile)


#if opts.options.dolegend:
#    PyGMT.colourkey(area,var.colourmap.cptfile,title=var.long_name,pos=[0,-2])
    
plot.close()
