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

"""Plot EISMINT test results."""

# some configuration
Width=18.
ProfileHeight=2.5
SpotHeight=3.5

import PyGMT,PyCF,sys, numpy

parser = PyCF.CFOptParser()
parser.profile(vars=False)
parser.add_option("--pmt",action="store_true", dest="pmt",default=False,help='Correct temperature for temperature dependance on pressure')
parser.time()
parser.plot()
opts = PyCF.CFOptions(parser,2)
infile = opts.cfprofile()
time = opts.times(infile,0)

Labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
divide   = [len(infile.file.variables['x1'][:])/2,len(infile.file.variables['y1'][:])/2]
midpoint = [3*len(infile.file.variables['x1'][:])/4,len(infile.file.variables['y1'][:])/2]
spots = [divide,midpoint]

spots_loc = []
for i in range(0,len(spots)):
    spots_loc.append([infile.file.variables['x1'][spots[i][0]],infile.file.variables['y1'][spots[i][1]]])

plot = opts.plot()
plot.defaults['LABEL_FONT_SIZE']='12p'
plot.defaults['ANNOT_FONT_SIZE']='10p'
bigarea = PyGMT.AreaXY(plot,size=opts.papersize,pos=[0,0])

ypos = 26.

# plot title and stuff
textheight=1.2
ypos = ypos-textheight            
area=PyGMT.AreaXY(bigarea,pos=[0.,ypos],size=[Width,textheight])
area.text([0.,textheight],infile.title,'18 0 0 TL',comargs='-N')
area.text([Width,textheight],'%.2f ka'%infile.time(time),'18 0 0 TR',comargs='-N')
if hasattr(infile,'comment'):
    if len(infile.comment)>0:
        area.text([0.,0.],infile.comment,'14 0 0 LB',comargs='-N')

# plot ice surface and basal temperatures
deltay = 0.7
mapheight = Width/3.-deltay
ypos = ypos - mapheight - .5
thk = infile.getvar('thk')
area = PyCF.CFArea(bigarea,infile,pos=[0.,ypos],size=mapheight)
area.axis='WeSN'
area.image(thk,time,clip = 'thk')
area.coordsystem()
area.profile(args='-W5/0/0/0')
for i in range(0,len(spots)):
    area.plotsymbol([spots_loc[i][0]],[spots_loc[i][1]],size='0.3',symbol='a',args='-G%s'%PyCF.CFcolours[i])
    area.text(spots_loc[i],'%s'%Labels[i],'12 0 0 MC',comargs='-D0/0.4')
area.stamp(thk.long_name)

btmp = infile.getvar('temp')
btmp.pmt = opts.options.pmt
area = PyCF.CFArea(bigarea,infile,pos=[mapheight+deltay,ypos],size=mapheight)
area.axis='wESN'
area.image(btmp,time,clip = 'thk',level=-1)
area.coordsystem()
area.profile(args='-W5/0/0/0')
for i in range(0,len(spots)):
    area.plotsymbol([spots_loc[i][0]],[spots_loc[i][1]],size='0.3',symbol='a',args='-G%s'%PyCF.CFcolours[i])
    area.text(spots_loc[i],'%s'%Labels[i],'12 0 0 MC',comargs='-D0/0.4')
area.stamp(btmp.long_name)

# plot some stats
area = PyGMT.AreaXY(bigarea,pos=[2*(mapheight+deltay)+0.3,ypos],size=[mapheight+0.5,mapheight])
area.text([0.,mapheight],'Ice thickness at divide: %.2fm'%thk.getSpotIJ(divide,time=time),'12 0 0 TL',comargs='-N')
area.text([0.,mapheight-.5],'Basal temp at divide: %.2fC'%btmp.getSpotIJ(divide,time=time,level=-1),'12 0 0 TL',comargs='-N')
area.text([0.,mapheight-1.],'Basal temp at midpnt: %.2fC'%btmp.getSpotIJ(midpoint,time=time,level=-1),'12 0 0 TL',comargs='-N')
# plot colour keys
PyGMT.colourkey(area,thk.colourmap.cptfile,title=thk.long_name,pos=[0,3],size=[mapheight+0.5,0.4])
PyGMT.colourkey(area,btmp.colourmap.cptfile,title=btmp.long_name,pos=[0,1],size=[mapheight+0.5,0.4])

# plot profiles
thk_prof = infile.getprofile('thk')
horiz_prof = infile.getprofile('uvel_avg')
btmp_prof = infile.getprofile('temp')
btmp_prof.pmt=opts.options.pmt

ypos = ypos-3*ProfileHeight-2.
area = PyCF.CFProfileMArea(bigarea,pos=[2.,ypos],size=[Width-3.,ProfileHeight])
area.newprof(horiz_prof,time)
area.newprof(btmp_prof,time,level=-1)
area.newprof(btmp_prof,time)
area.finalise(expandy=True)
area.coordsystem()

# plot temperature profiles
profx = (Width-1)/3.-deltay
ypos = ypos - SpotHeight - 2.
area = PyGMT.AutoXY(bigarea,size=[profx,SpotHeight],pos=[1.,ypos])
area.axis='WeSn'
for i in range(0,len(spots)):
    data = btmp.getSpotIJ(spots[i],time,level=None)
    area.line('-W1/%s'%PyCF.CFcolours[i],data,(1-infile.file.variables['level'][:]))
area.xlabel = '%s [%s]'%(btmp.long_name,btmp.units)
area.ylabel = 'normalised height'
area.finalise(expandx=True)
area.coordsystem()

wvel = infile.getvar('wvel')
area = PyGMT.AutoXY(bigarea,size=[profx,SpotHeight],pos=[profx+1.5,ypos])
area.axis='weSn'
for i in range(0,len(spots)):
    data = wvel.getSpotIJ(spots[i],time,level=None)
    area.line('-W1/%s'%PyCF.CFcolours[i],data,(1-infile.file.variables['level'][:]))
area.xlabel = '%s [%s]'%(wvel.long_name,wvel.units)
area.finalise(expandx=True)
area.coordsystem()

uvel = infile.getvar('uvel')
area = PyGMT.AutoXY(bigarea,size=[profx,SpotHeight],pos=[2*profx+2.,ypos])
area.axis='wESn'
for i in range(0,len(spots)):
    d1 = uvel.getSpotIJ(spots[i],time,level=None)
    d2 = uvel.getSpotIJ([spots[i][0]-1,spots[i][1]],time,level=None)
    data = (numpy.array(d1)+numpy.array(d2))/2.
    area.line('-W1/%s'%PyCF.CFcolours[i],data,(1-infile.file.variables['level'][:]))
area.xlabel = '%s [%s]'%(uvel.long_name,uvel.units)
area.finalise(expandx=True)
area.coordsystem()

# plot keys
#area = PyGMT.KeyArea(bigarea,pos=[2*profx+3.,ypos],size=[profx,SpotHeight])
#area.num = [1,5]
#for i in range(0,len(spots)):
#    area.plot_line('%s [%d,%d]'%(Labels[i],spots[i][0],spots[i][1]),'1/%s'%PyCF.CFcolours[i])

# plot ice volume and area
# changed to plot ice thickness and basal temp at divide
ypos = ypos-ProfileHeight-2.4
#ice_area = infile.getIceArea()
#ice_vol = infile.getIceVolume()
area = PyCF.CFAreaTS(bigarea,size=[Width-1.,ProfileHeight],pos=[1.,ypos])

#ia = area.newts()
#ia.xlabel = 'time [ka]'
#ia.ylabel = '%s [%s]'%(btmp.long_name,btmp.units)
#for i in range(0,len(spots)):
#    div_btemp = btmp.getSpotIJ(spots[i],level=-1)
#    ia.line('-W1/%s'%PyCF.CFcolours[i],infile.time(None),div_btemp)
#ia.ylabel = 'ice area'
#ia.line('-W1/0/0/0',infile.time(None),ice_area)

iv = area.newts()
iv.xlabel = 'time [ka]'
iv.ylabel = '%s [%s]'%(thk.long_name,thk.units)
for i in range(0,len(spots)):
    div_thick = thk.getSpotIJ(spots[i])
    iv.line('-W1/%s'%PyCF.CFcolours[i],infile.time(None),div_thick)
#iv.ylabel = 'ice volume'
#iv.line('-W1/0/0/0',infile.time(None),ice_vol)

area.finalise(expandy=True)
area.coordsystem()
area.time(infile.time(time))

plot.close()
