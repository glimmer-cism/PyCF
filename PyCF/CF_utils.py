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

"""Useful utility functions."""

__all__ = ['CFinterpolate_xy','CFinterpolate_linear','CFstat_names','CFgetstats','CFdatadir']

import math, Numeric,os

# setting up PyCF data path
try:
    CFdatadir=os.environ['GLIMMER_PREFIX']
except:
    raise RuntimeError, 'Set GLIMMER_PREFIX to where glimmer is installed.'
CFdatadir = os.path.join(CFdatadir,'share','PyCF')
if not os.path.exists(CFdatadir):
            raise RuntimeError, 'Error, cannot find %s,\nPyCF is not installed properly.'%CFdatadir

CFstat_names = ["Volume [10^6km^3]:","Area [10^6km^2]:","Melt Frac:\t","Divide thick [m]:","Divide btemp [degC]:"]

def CFgetstats(cffile,time, eismint=False):
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

def CFinterpolate_xy(profile,interval):
    "linearly interpolate profile, return interpolated array and number of points outside region"

    data = []
    p = Numeric.array(profile)
    for i in range(0,len(p[0,:])):
        data.append([float(p[0,i]),float(p[1,i])])
    remainder = lr = 0.
    d0 = data[0]
    ix = []
    iy = []
    ix.append(d0[0])
    iy.append(d0[1])

    for d in data[1:]:
        x = d[0] - d0[0]
        y = d[1] - d0[1]
        dist = math.sqrt(x*x + y*y)
        remainder = remainder + dist
        cm = x/dist
        sm = y/dist
        while (remainder - interval) >= 0.:
            d0[0] = d0[0] + (interval-lr)*cm
            d0[1] = d0[1] + (interval-lr)*sm
            lr = 0.
            ix.append(d0[0])
            iy.append(d0[1])
            remainder = remainder - interval
        lr = remainder
        d0 = d    
    
    return Numeric.array([ix,iy],Numeric.Float32)

def CFinterpolate_linear(x,y,pos):
    """Linear interpolation.

    x,y: data points
    pos: list of new x positions onto which y should be interpolated.

    we assume monotonic sequences in x and pos"""

    if len(x)!=len(y):
        raise ValueError, 'x and y are not of the same length.'

    res = []
    j = 0
    for i in range(0,len(pos)):
        # boundary conditions
        if pos[i] <= x[0]:
            res.append(y[0])
            continue
        if pos[i] >= x[-1]:
            res.append(y[-1])
            continue
        while (pos[i]>x[j]):
            j = j + 1
        res.append(y[j-1]+(pos[i]-x[j-1])*(y[j]-y[j-1])/(x[j]-x[j-1]))
    return res
