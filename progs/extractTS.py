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

"""Extract time series from netCDF file"""

import PyCF,sys

# creating option parser
parser = PyCF.CFOptParser()
parser.spot()
parser.add_option("--volume",default=False,action="store_true",help="extract ice volume")
parser.add_option("--area",default=False,action="store_true",help="extract area covered by ice")
parser.add_option("--melt",default=False,action="store_true",help="extract melt fraction area")
parser.add_option("--extent",default=False,action="store_true",help="extract ice extent along profile")
parser.profile_file()
#parser.time()
opts = PyCF.CFOptions(parser,2)

if opts.options.extent:
    try:
        infile = opts.cfprofile()
    except:
        print 'Error, need to specify a profile line when extracting ice extent'
        sys.exit(1)
else:
    infile = opts.cffile()

outfile = open(opts.args[-1],'w')
# write header
outfile.write('# file:\t\t%s\n# title:\t%s\n# comment:\t%s\n'%(opts.args[-2],infile.title,infile.comment))
headers = '#time'
time = infile.time(None)
if opts.options.volume:
    headers+='\tvolume'
    volume = infile.getIceVolume()
if opts.options.area:
    headers+='\tarea'
    area = infile.getIceArea()
if opts.options.melt:
    headers+='\tmelt_f'
    melt = infile.getFracMelt()
if opts.options.extent:
    headers+='\textent'
    extent = infile.getExtent()
if opts.options.vars != None:
    variables = []
    for i in range(0,opts.nvars):
        var = opts.vars(infile,i)
        headers+='\t%s'%var.name
        variables.append(var.getSpotIJ(opts.options.ij[0],level=opts.options.level))
headers+='\n'
outfile.write(headers)

for t in range(0,len(time)):
    data = '%f'%time[t]
    if opts.options.volume:
        data+='\t%f'%volume[t]
    if opts.options.area:
        data+='\t%f'%area[t]
    if opts.options.melt:
        data+='\t%f'%melt[t]
    if opts.options.extent:
        data+='\t%f'%extent[t]
    if opts.options.vars != None:
        for i in range(0,len(variables)):
            data+='\t%f'%variables[i][t]
    data+='\n'
    outfile.write(data)

outfile.close()
infile.close()
