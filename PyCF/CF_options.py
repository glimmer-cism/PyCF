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

"""Handle command line options in a standard way."""

__all__ = ['CFOptParser','CFOptions']

import optparse, PyGMT
from CF_loadfile import *

class CFOptParser(optparse.OptionParser):
    """Handle options."""

    def __init__(self,usage = "usage: %prog [options] infile outfile"):
        """Initialise.

        usage: usage string.
        """
        optparse.OptionParser.__init__(self,usage)

        self.width = 10.
        
        
    def plot(self):
        """Plot options."""

        group = optparse.OptionGroup(self,"Plot Options","These options are used to control the appearance of the plot")
        group.add_option("--size",dest="size",default="a4",help="Size of output (default a4)")
        group.add_option("--landscape",action="store_true", dest="landscape",help="select landscape mode")
        group.add_option("--width",type="float",dest="width",default=self.width, help="width of plot (default %.2f cm)"%(self.width))
        group.add_option("--verbose",action="store_true", dest="verbose",default=False,help="Be verbose")
        self.add_option_group(group)

    def region(self):
        """Specifying region of interest."""

        group = optparse.OptionGroup(self,"Region Options","These options are used to control the region of interest.")
        group.add_option("--llx",dest='llx',metavar="X Y",type="float",nargs=2,help="lower left corner in projected coordinate system")
        group.add_option("--urx",dest='urx',metavar="X Y",type="float",nargs=2,help="upper right corner in projected coordinate system")
        group.add_option("--llg",dest='llg',metavar="X Y",type="float",nargs=2,help="lower left corner in geographic coordinate system")
        group.add_option("--urg",dest='urg',metavar="X Y",type="float",nargs=2,help="upper right corner in geographic coordinate system")
        self.add_option_group(group)

    def variable(self):
        """Variable option."""

        self.add_option("-v","--variable",metavar='NAME',action='append',type="string",dest='vars',help="variable to be processed (this option can be used more than once)")

    def time(self):
        """Time option."""
        self.add_option("-t","--time",metavar='TIME',action='append',type="float",dest='times',help="time to be processed (this option can be used more than once)")


class CFOptions(object):
    """Do some option/argument massaging."""

    def __init__(self,parser):
        """Initialise.

        parser: Option parser."""

        (self.options, self.args) = parser.parse_args()

    def plot(self,argn=-1):
        """Setup plot.

        argn: number of argument holding output name."""

        if self.options.landscape:
            orientation = "landscape"
        else:
            orientation = "portrait"

        plot = PyGMT.Canvas(self.args[argn],size=self.options.size,orientation=orientation)
        if self.options.verbose:
            plot.verbose = True
        return plot

    def cffile(self,argn=0):
        """Load CF file.

        argn: number of argument holding CF file name."""

        infile = CFloadfile(self.args[argn])

        if hasattr(self.options,'llx'):
            if self.options.llx != None:
                infile.ll_xy = self.options.llx
        if hasattr(self.options,'urx'):
            if self.options.urx != None:
                infile.ur_xy = self.options.urx
        if hasattr(self.options,'llg'):
            if self.options.llg != None:
                infile.ll_geo = self.options.llg
        if hasattr(self.options,'urg'):
            if self.options.urg != None:
                infile.ur_geo = self.options.urg
        
        return infile

    def vars(self,cffile,varn=0):
        """Get variable.

        varn: variable number
        """
        return CFvariable(cffile,self.options.vars[varn])

    def times(self,cffile,timen=0):
        """Get time slice.

        timen: time number."""

        if self.options.times != None:
            return cffile.timeslice(self.options.times[timen])
        else:
            return 0
