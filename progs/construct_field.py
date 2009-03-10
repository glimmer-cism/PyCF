#!/usr/bin/env python

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

"""Construct a field based on polygons."""

import PyCF, numpy, sys, datetime
from optparse import OptionParser

try:
    import Polygon
except:
    print """You must have installed the polygon clipping module, which you can get from here
    http://www.dezentral.de/warp.html?http://www.dezentral.de/soft/Polygon/index.html"""
    sys.exit(1)

def smooth_field(field,num):
    """Smooth field with size num moving average filter."""

    numx = field.shape[1]
    numy = field.shape[0]

    outfield = numpy.zeros(field.shape,'f')

    for j in range(0,numy):
        for i in range(0,numx):
            total = 0.
            s = 0
            for n in range(max(0,j-num),min(numy-1,j+num)):
                for m in range(max(0,i-num),min(numx-1,i+num)):
                    total = total + field[n,m]
                    s = s+1
            if n>0:
                outfield[j,i] = total/s
    return outfield

if __name__ == '__main__':
    parser = OptionParser(usage="%prog [options] inputnc outputnc",description="Construct a field base on input file and a polygon.")
    parser.add_option("-v","--variable",default='cony',metavar='NAME',type="string",help="variable to be processed")
    parser.add_option("-t","--time",metavar='TIME',type="float",dest='times',help="time to be processed (this option can be used more than once)")
    parser.add_option("-T","--timeslice",metavar='N',type="int",help="time slice to be processed (this option can be used more than once)")
    parser.add_option("-f","--file",metavar='NAME',help="read contours from file")
    parser.add_option("-p","--vertex",metavar="LON LAT",nargs=2,action="append",type="float",help="Coordinates of point on line, this option can be used more than once.")
    parser.add_option("-i","--inside",metavar="VAL",type="float",help="Set field to VAL inside polygon")
    parser.add_option("-o","--outside",metavar="VAL",type="float",help="Set field to VAL outside polygon")
    parser.add_option("-s","--smooth",metavar="DIST",type="float",help="Smooth resulting field using a running average filter of size DIST [km]")
    parser.add_option("--title",type="string",help="Set title")
    parser.add_option("--institution",type="string",help="Set institution")
    parser.add_option("--source",type="string",help="Set source")
    parser.add_option("--references",type="string",help="Set references")
    parser.add_option("--comment",type="string",help="Set comment")
   
    (options, args) = parser.parse_args()
    if len(args)!=2:
        parser.error('Need to specify both an input and an output netCDF file')


    # create output file
    infile = PyCF.CFloadfile(args[0])
    outfile = infile.clone(args[1])
    if options.title != None:
        outfile.title = options.title
    if options.institution != None:
        outfile.institution = options.institution
    if options.source != None:
        outfile.source = options.source
    if options.references != None:
        outfile.references = options.references
    if options.comment != None:
        outfile.comment = options.comment
    args = ''
    for a in sys.argv:
        args = '%s %s '%(args,a)
    outfile.history = '%s: %s'%(datetime.datetime.today(),args)
    outvar = outfile.createVariable(options.variable)
    xdim = outfile.file.variables[outvar.dimensions[-1]]
    ydim = outfile.file.variables[outvar.dimensions[-2]]

    # see if input file contains selected variable
    try:
        var = infile.getvar(options.variable)
        t = 0
        if options.times != None:
            t = infile.timeslice(options.times)
        elif options.timeslice !=None:
            t = options.timeslice
        invar = var.get2Dfield(t)    
    except KeyError:
        invar = None
        t = None
    if t!=None:
        outfile.file.variables['time'][0] = infile.file.variables['time'][t]
    else:
        outfile.file.variables['time'][0] = 0
    if invar!=None:
        outvar[0,:,:] = numpy.transpose(invar[:,:])
    else:
        if options.outside!=None:
            outvar[0,:,:] = options.outside
        else:
            outvar[0,:,:] = 0.

    # construct polygon from vertecies
    poly = []
    inside = []
    if options.vertex!=None:
        points = options.vertex
        # project points into cartesian coords
        for i in range(0,len(points)):
            points[i] = outfile.project(list(points[i]))
            
        # close polygon
        points.append(points[0])
        # create polygon
        poly.append(Polygon.Polygon(points))
        inside.append(options.inside)
        

    if options.file!=None:
        cntrs = PyCF.CFcontours(open(options.file,'r'))
        for k in range(0,len(cntrs)):
            points = cntrs[k]['vert']
            for i in range(0,len(points)):
                points[i] = outfile.project(list(points[i]))
            points.append(points[0])
            poly.append(Polygon.Polygon(points))
            inside.append(cntrs[k]['val'])

    if len(poly)>0:
        #loop over region
        for j in range(0,len(ydim[:])):
            for i in range(0,len(xdim[:])):
                p_is_outside=True
                for k in range(0,len(poly)):
                    if poly[k].isInside(xdim[i],ydim[j]):
                        if inside[k]!=None:
                            outvar[0,j,i] = inside[k]
                        p_is_outside=False

    # check if we should smooth results
    if options.smooth != None:
        num = int(options.smooth*500./(xdim[1]-xdim[0])+0.5)
        outvar[0,:,:] = smooth_field(outvar[0,:,:],num)

    infile.close()
    outfile.close()
    
