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

__all__ = ['CFinterpolate_xy']

import math, Numeric

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
