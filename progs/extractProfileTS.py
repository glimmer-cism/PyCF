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

"""extract data along profile for a time interval."""

import PyGMT,PyCF,numpy,sys

# creating option parser
parser = PyCF.CFOptParser()
parser.profile()
parser.timeint()
opts = PyCF.CFOptions(parser,2)
infile = opts.cfprofile()
time = opts.times(infile,0)

try:
    t0 = opts.times(infile,0)
    t1 = opts.times(infile,1)
except:
    t0=0
    t1=infile.numt-1

if opts.nvars>1:
    print 'Warning, more than one variable requested, only processing first one.'


outfile = open(opts.args[-1],'w')
outfile.write('# file:\t\t%s\n# title:\t%s\n# variable:\t\t%s\n'%(opts.args[-2],infile.title,opts.options.vars[0]))
# write distances along profile
outfile.write('     ')
for x in range(0,len(infile.xvalues)):
    outfile.write(', %f'%infile.xvalues[x])
outfile.write('\n')

profile = opts.profs(infile)
for t in range(t0,t1):
    data = profile.getProfile(t,level=opts.options.level)
    outfile.write('%f'%infile.time(t))
    for x in range(0,len(infile.xvalues)):
        outfile.write(', %f'%data[x])
    outfile.write('\n')

outfile.close()
