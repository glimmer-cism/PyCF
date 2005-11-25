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

import PyCF,PyGMT

DIFF_VARS=['bvel','bmlt','btemp','topg','thk']
DONT_CLIP=['topg']

def compare(inname1,inname2,plot,timeint):
    """Compare two CF files and produce graphical output."""

    cf1 = PyCF.CFloadfile(inname1)
    cf2 = PyCF.CFloadfile(inname2)

    if timeint != None:
        times = [cf1.timeslice(timeint[0]), cf1.timeslice(timeint[1])]
    else:
        times = None

    plot.defaults['LABEL_FONT_SIZE']='12p'
    plot.defaults['ANOT_FONT_SIZE']='10p'
    bigarea = PyGMT.AreaXY(plot,size=[20,30])

    area = PyCF.CFdiff(bigarea,cf1,cf2,times)
    for v in DIFF_VARS:
        if v in cf1.file.variables.keys() and v in cf2.file.variables.keys():
            if v in DONT_CLIP:
                area.plothist(v)
            else:
                area.plothist(v,clip='thk')
    if 'bmlt' in cf1.file.variables.keys() and 'bmlt' in cf2.file.variables.keys():
        area.plotmelt()
    area.plotarea()
    area.plotvol()
    area.finalise(expandy=True)
    area.coordsystem()

    plot.close()
    

if __name__ == '__main__':

    parser = PyCF.CFOptParser(usage = "usage: %prog [options] infile1 infile2 outfile")
    parser.timeint()
    parser.plot()
    opts = PyCF.CFOptions(parser,3)

    plot=opts.plot()

    compare(opts.args[0],opts.args[1],plot,opts.options.times)
