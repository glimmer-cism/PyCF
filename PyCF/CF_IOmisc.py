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

"""Miscellaneous I/O operations."""

__all__ = ['CFTimeSeries','CFEIStemp']

import Numeric, math

class CFTimeSeries(object):
    """Handling time series."""

    def __init__(self,fname,sep=None,timescale = 0.001):
        """Initialise

        fname: name of file to read from.
        sep:   separator (whitespace if set to none
        timescale: scale time"""

        infile = open(fname,'r')
        self.timescale = 0.001
        stime = []
        sdata = []
        self.numt = 0
        self.__index = 0
        for line in infile.readlines():
            pos = line.find('#')
            if pos>-1:
                line = line[:pos]
            line = line.strip()
            if len(line) == 0:
                continue
            if sep == None:
                l = line.split()
            else:
                l = line.split(sep)
            stime.append(float(l[0])*self.timescale)
            data = []
            for d in l[1:]:
                d = float(d)
                data.append(d)
            sdata.append(data)
            self.numt = self.numt + 1
        self.time = Numeric.array(stime)
        self.data = Numeric.array(sdata)

    def get_index(self,time):
        """Find index i so that t[i] <= time < t[i+1].

        time: time to find."""

        # BC
        if time <= self.time[0]:
            return 0
        if time >= self.time[self.numt-1]:
            return self.numt-1
        # check if time is around index
        if (time>=self.time[self.__index] and time<self.time[self.__index+1]):
            return self.__index
        # no, let's try the next interval
        self.__index = self.__index + 1
        if (time>=self.time[self.__index] and time<self.time[self.__index+1]):
            return self.__index
        # no, ok let's search for it using Newton
        lower = 1
        upper = self.numt-1
        while True:
            self.__index = lower + int((upper-lower)/2)
            if (time>=self.time[self.__index] and time<self.time[self.__index+1]):
                return self.__index
            if (time > self.time[self.__index]):
                lower = self.__index
            else:
                upper = self.__index
                
    def step(self,time):
        """Interpolate time series by stepping.

        time: time to get
        index: extract particular index, return array if index==None."""

        i = self.get_index(time)
        return self.data[i,:]

    def linear(self,time,index=None):
        """Linearly interpolating time series.

        time: time to get
        index: extract particular index, return array if index==None."""
        
        i = self.get_index(time)
        if i==0 or i==self.numt-1:
            data = self.data[i]
        else:
            d1 = self.data[i,:]
            d2 = self.data[i+1,:]
            factor = (time-self.time[i])/(self.time[i+1]-self.time[i])
            data = []
            for j in range(0,len(d1)):
                data.append(d1[j]+factor*(d2[j]-d1[j]))
        return Numeric.array(data)


class CFEIStemp(CFTimeSeries):
    """Handling EIS temperature forcing."""

    def __init__(self,fname,lat=60.,sep=None,timescale = 0.001,temp_type='poly',lat0 = 44.95):
        """Initialise

        fname: name of file to read from.
        lat: latitude
        sep:   separator (whitespace if set to none
        timescale: scale time
        temp_type: select temp distribution function, can be poly (default) or exp
        lat0: parameter used for exponential function (default: 44.95)"""

        CFTimeSeries.__init__(self,fname,sep=sep,timescale=timescale)
        sdata = []
        for j in range(0,len(self.data)):
            val = self.data[j]
            t = 0.
            if temp_type == 'poly':
                l = 1.
                for i in range(0,len(val)):
                    t = t + l*val[i]
                    l = l*lat
            elif temp_type == 'exp':
                t = val[0]+val[1]*math.exp(val[2]*(lat-lat0))
            else:
                raise RuntimeError, 'No handle for temperature calculations type=\'%s\''%temp_type
            sdata.append([t])
        self.data = Numeric.array(sdata)
