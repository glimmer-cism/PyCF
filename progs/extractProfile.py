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

"""extract data along profile."""

import PyGMT,PyCF,Numeric,sys

# creating option parser
parser = PyCF.CFOptParser()
parser.profile()
parser.time()
opts = PyCF.CFOptions(parser,2)
infile = opts.cfprofile()
time = opts.times(infile,0)

# extracting data
data = []
vars = []

data.append(infile.xvalues)
vars.append('# dist')
for i in range(0,opts.nvars):
    profile = opts.profs(infile,i)
    if profile.average:
        vars.append('%s_avg'%profile.name)
    else:
        vars.append(profile.name)
    data.append(profile.getProfile(time,level=opts.options.level))

# writing data to file
outfile = open(opts.args[-1],'w')
outfile.write('# file:\t\t%s\n# title:\t%s\n# time:\t\t%f\n'%(opts.args[-2],infile.title,infile.time(time)))
for v in vars:
    outfile.write('%s\t\t'%v)
outfile.write('\n')
for x in range(0,len(infile.xvalues)):
    for d in data:
        outfile.write('%f\t'%d[x])
    outfile.write('\n')


outfile.close()
