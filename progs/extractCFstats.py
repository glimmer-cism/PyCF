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

"""get some statistics of an ice sheet."""

import PyCF,sys, Numeric

stat_names = ["Volume [10^6km^3]:","Area [10^6km^2]:","Melt Frac:\t","Divide thick [m]:","Divide btemp [degC]:"]

def getstats(cffile,time, eismint=False):
    """Get ice statistics.

    cffile: CF file object
    time: time slice to be processed
    eismint: set to True if it's an EISMINT 2 test (default: False)

    returns a Numeric array: [volume, area, melt fraction]
    if it's an eismint 2 file, then the array contains additionally [...,divide thickness,divide basal temp]"""

    if eismint:
        stats = Numeric.zeros([5],Numeric.Float)
    else:
        stats = Numeric.zeros([3],Numeric.Float)
    stats[0] = cffile.getIceVolume(time=time,scale=1.e-15)
    stats[1] = cffile.getIceArea(time=time,scale=1.e-12)
    stats[2] = cffile.getFracMelt(time=time)
    if eismint:
        divide   = [len(cffile.file.variables['x1'][:])/2,len(cffile.file.variables['y1'][:])/2]
        thick = cffile.getvar('thk')
        stats[3] = thick.getSpotIJ(divide,time=time)
        temp = cffile.getvar('temp')
        stats[4] = temp.getSpotIJ(divide,time=time,level=-1)
    return stats

if __name__ == '__main__':
    # creating option parser
    parser = PyCF.CFOptParser(usage = """usage: %prog [options] infile1 [infile2 ... infileN] [compfile]
    prints statistics of ice sheet and (if given) compares them with statistics of compfile""")
    parser.time()
    opts = PyCF.CFOptions(parser,-1)

    if len(opts.args) > 1:
        cffile = opts.cffile(-1)
        time = opts.times(cffile)
        stats_comp = getstats(cffile,time,True)
        comp_title = cffile.title
    else:
        stats_comp = None

    numfiles = len(opts.args)
    if numfiles > 1:
        numfiles = numfiles -1

    for i in range(0,numfiles):
        cffile = opts.cffile(i)
        time = opts.times(cffile)
        stats = getstats(cffile,time,True)
        out = []
        out.append("\t\t\t%s"%cffile.title)
        for i in range(0,len(stats)):
            out.append("%s\t%f"%(stat_names[i],stats[i]))
        if stats_comp != None:
            out[0] = out[0]+'\t rel to %s'%comp_title
            for i in range(0,len(stats)):
                if i==4:
                    out[i+1] = out[i+1]+'\t %f'%(stats[i]-stats_comp[i])
                else:
                    out[i+1] = out[i+1]+'\t %f%%'%(100.*(stats[i]-stats_comp[i])/(abs(stats_comp[i])))
                
        for l in out:
            print l
        print ''
