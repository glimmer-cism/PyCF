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

"""extract 2D data along profile."""

import PyGMT,PyCF,numpy,sys

# creating option parser
parser = PyCF.CFOptParser()
parser.add_option("-H",type="float",dest="hlevel",action='append',help="extract data from this ice level in metres above 0")
parser.profile()
parser.time()
opts = PyCF.CFOptions(parser,2)
infile = opts.cfprofile()
time = opts.times(infile,0)
profile = opts.profs(infile)
if not profile.is3d:
    print 'Selected variable %s is not 3D'%profile.name
    sys.exit(1)

# extract data
hlevel = opts.options.hlevel
level = profile.file.variables['level']
data = []
for l in range(0,len(level)):
    data.append(profile.getProfile(time,level=l))
thick = infile.getprofile('thk').getProfile(time)


# writing data to file
outfile = open(opts.args[-1],'w')
outfile.write('# file:\t\t%s\n# title:\t%s\n# time:\t\t%f\n'%(opts.args[-2],infile.title,infile.time(time)))

if hlevel==None:
    outfile.write('#levels:\t\t')
    for l in range(0,len(level)):
        outfile.write('\t%f'%level[l])
    outfile.write('\n')
    outfile.write('#x\t\tthick\n')
    for i in range(0,len(infile.xvalues)):
        outfile.write('%f\t%f'%(infile.xvalues[i],thick[i]))
        for l in range(0,len(level)):
            outfile.write('\t%f'%data[l][i])
        outfile.write('\n')
else:
    outfile.write('#ice_layer:\t\t')
    for l in range(0,len(hlevel)):
        outfile.write('\t%f'%hlevel[l])
    outfile.write('\n')
    outfile.write('#x\t\tthick\n')
    for i in range(0,len(infile.xvalues)):
        outfile.write('%f\t%f'%(infile.xvalues[i],thick[i]))
        for l in range(0,len(hlevel)):
            if hlevel[l]<0. or hlevel[l]>thick[i]:
                hdata = 'NaN'
            elif hlevel[l]==0.:
                hdata = '%f'%data[-1][i]
            else:
                for lev in range(len(level)-1,0,-1):
                    if hlevel[l]<(1.-level[lev])*thick[i]:
                        break
                hdata = '%f'%(data[lev+1][i]+hlevel[l]/thick[i]*(data[lev][i]-data[lev+1][i])/(level[lev+1]-level[lev]))
            outfile.write('\t%s'%hdata)
        outfile.write('\n')
                
        
outfile.close()
