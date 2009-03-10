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

"""Class for plotting ISM grid files."""

__all__ = ['CFArea']

import PyGMT,numpy,math,tempfile, os.path
from PyGMT import gridcommand
from CF_loadfile import CFvariable
from CF_colourmap import CFcolours
from StringIO import StringIO
from CF_utils import CFdatadir

class CFArea(PyGMT.AreaXY):
    """CF grid plotting area."""

    def __init__(self,parent,cffile,pos=[0.,0.],size=10):
        """Initialising ISM area.

        parent: can be either a Canvas or another Area.
        cffile: CF file used for setting up projection and area
        pos: position of area relative to the parent
        size: size of GMT area
        """

        # initialising geographic area
        self.file = cffile
        if cffile.projection == 'lin':
            self.geo = PyGMT.AreaXY(parent,pos=pos,size=[size,cffile.aspect_ratio*size])
            self.geo.setregion([cffile.ll_geo[0]/10000.,cffile.ll_geo[1]/10000.], [cffile.ur_geo[0]/10000.,cffile.ur_geo[1]/10000.])
        else:
            self.geo = PyGMT.AreaGEO(parent,cffile.projection.getGMTprojection(mapwidth=size).upper(), pos=pos, size=size)
            self.geo.setregion(cffile.ll_geo, cffile.ur_geo)
        # initialising paper area
        self.paper = PyGMT.AreaXY(parent,pos=pos,size=self.geo.size)

        # initialising XY area
        PyGMT.AreaXY.__init__(self,parent,pos=pos,size=self.geo.size)
        self.setregion(cffile.ll_xy, cffile.ur_xy)

    def coordsystem(self,grid=True):
        """Plot coordinate system.

        grid: if true plot lat/long grid"""
        self.geo.axis = self.axis
        self.geo.coordsystem(grid=grid)

    def coastline(self,args='-W -A0/1/1',resolution='l'):
        """Plot coastline.

        args: arguments passed on to pscoast.
        resolution: resolution of coastline data to be used, can be f,h,l,c"""

        a = '%s -D%s'%(args,resolution)
        try:
            self.geo.coastline(a)
        except:
            pass

    def stamp(self,text):
        """Print text in lower left corner."""

        self.paper.text([0.15,0.15],text,textargs='8 0 0 LB',comargs='-W255/255/255o')

    def printinfo(self,time):
        """Print a data name and time slice."""

        self.stamp('%s   %.2fka'%(self.file.title,self.file.time(time)))

    def image(self,var,time,level=0,clip=None,mono=False,illuminate=None):
        """Plot a colour map.

        var: CFvariable
        time: time slice
        level: horizontal slice
        clip: only display data where clip>0.
        mono: convert colour to mono
        illuminate: azimuth of light source (default None)
        """

        self.raw_image(var.cffile,time,var.getGMTgrid(time,level=level),var.colourmap.cptfile,var.isvelogrid,clip,mono,illuminate)
        
    def raw_image(self,cffile,time,grid,colourmap,isvelogrid=False,clip=None,mono=False,illuminate=None):
        """Plot a GMT grid
        
        cffile: cffile
        time: time slice
        grid: is the GMT grid to be plotted
        isvelogrid: boolean whether we are plotting on velogrid
        colourmap: is the colourmap to be used
        clip: only display data where clip>0.
        mono: convert colour to mono
        illuminate: azimuth of light source (default None)
        """

        clipped = False
        if clip in ['topg','thk','usurf','is'] :
            cvar = CFvariable(cffile,clip)
            self.clip(cvar.getGMTgrid(time),0.1)
            clipped = True
        if mono:
            args="-M"
        else:
            args=""

        illu = False
        if illuminate in ['topg','thk','usurf','is'] :
            illu = True
            illu_var = CFvariable(cffile,illuminate)
            illu_grd = illu_var.getGMTgrid(time,velogrid=isvelogrid)
            illu_file = tempfile.NamedTemporaryFile(suffix='.grd')
            illu_arg = "=bf -G%s -A0 -Ne0.6"%illu_file.name
            gridcommand('grdgradient',illu_arg,illu_grd,verbose=self.verbose)
            args = "%s -I%s"%(args,illu_file.name)
            
        PyGMT.AreaXY.image(self,grid,colourmap,args=args)
        if clipped:
            self.unclip()
        if illu:
            illu_file.close()
        
    def velocity_field(self,time,level=0,mins=10.):
        """Plot vectors of velocity field

        time: time slice
        level: horizontal slice
        mins: do not plot vectors below this size (default 0.01)
        """

        # get velocity components
        if 'uvel' in self.file.file.variables and 'vvel' in self.file.file.variables:
            velx = self.file.getvar('uvel')
            vely  = self.file.getvar('vvel')
            vel = self.file.getvar('vel')
        elif 'ubas' in self.file.file.variables and 'vbas' in self.file.file.variables:
            velx = self.file.getvar('ubas')
            vely  = self.file.getvar('vbas')
            vel = self.file.getvar('bvel')
        elif 'ubas_tavg' in self.file.file.variables and 'vbas_tavg' in self.file.file.variables:
            velx = self.file.getvar('ubas_tavg')
            vely  = self.file.getvar('vbas_tavg')
            vel = self.file.getvar('bvel_tavg')
            

        data = vel.get2Dfield(time,level=level)
        datax = velx.get2Dfield(time,level=level)
        datay = vely.get2Dfield(time,level=level)

        # calculate node spacing
        vector_density = 0.3
        x_spacing = int(((self.ur[0]-self.ll[0])/(self.size[0]*self.file.deltax))*vector_density)+1
        y_spacing = int(((self.ur[1]-self.ll[1])/(self.size[1]*self.file.deltay))*vector_density)+1

        fact = 360./(2*math.pi)
        outstring = StringIO()
        for i in range(int(self.ll[0]/self.file.deltax),int(self.ur[0]/self.file.deltax),x_spacing):
            for j in range(int(self.ll[1]/self.file.deltay),int(self.ur[1]/self.file.deltay),y_spacing):
                if (data[i,j]>mins):
                    outstring.write('%f %f %f %f\n'%(velx.xdim[i], velx.ydim[j], fact*math.atan2(datay[i,j],datax[i,j]), 0.3))

        self.canvascom('psxy',' -G0 -Sv0.01/0.1/0.1',indata=outstring.getvalue())
        
    def contour(self,var,contours,args,time,level=0,cntrtype='c'):
        """Plot a contour map.

        var: CFvariable
        contours: list of contour intervals
        args: further arguments
        time: time slice
        level: horizontal slice
        cntrtype: contourtype, c for normal contour, a for annotated"""

        PyGMT.AreaXY.contour(self,var.getGMTgrid(time,level=level),contours,args,cntrtype)

    def extent(self,args,time,cffile=None,cntrtype='c'):
        """Plot ice extent.

        args: further arguments
        time: time slice
        cntrtype: contourtype, c for normal contour, a for annotated"""

        if cffile == None:
            cffile = self.file
        extent = CFvariable(cffile,'thk').getGMTgrid(time)
        extent.data = extent.data - 0.1 + cffile.time(time)
        PyGMT.AreaXY.contour(self,extent,[cffile.time(time)],args,cntrtype)

    def land(self,time,grey='180',illuminate=None):
        """Plot area above sea level.

        time: time slice
        grey: grey value."""


        args=""

        cvar = CFvariable(self.file,'topg')
        cvar_grd = cvar.getGMTgrid(time)
        if illuminate in ['topg','thk','is'] :
            illu_file = tempfile.NamedTemporaryFile(suffix='.grd')
            illu_arg = "=bf -G%s -A0 -Ne0.6"%(illu_file.name)
            gridcommand('grdgradient',illu_arg,cvar_grd,verbose=self.verbose)
            args = "%s -I%s"%(args,illu_file.name)

        # create colour map
        cmap = tempfile.NamedTemporaryFile(suffix='.cpt')
        cmap.write('-15000 255     255     255  0 255     255     255\n')
        cmap.write('0 %s %s %s 10000  %s %s %s \n'%(grey,grey,grey,grey,grey,grey))
        cmap.flush()

        
        PyGMT.AreaXY.image(self,cvar_grd,cmap.name,args=args)
        cmap.close()

    def profile(self,args='-W1/0/0/0', prof=None, slabel=None, elabel=None):
        """Plot profile if present in file.

        args: pen arguments default -W1/0/0/0
        prof: instance of CFprofile class
        slabel: label to be printed at d=0
        elabel: label to be printed at d=-1"""

        if prof==None:
            if hasattr(self.file,'profiledata'):
                p = self.file.profiledata
            else:
                return
        else:
            p = prof
            
        self.line(args, p.interpolated[0,:].tolist(),p.interpolated[1,:].tolist())
        if slabel!=None:
            self.text(p.interpolated[:,0].tolist(),slabel,textargs='8 0 0 LB')
        if elabel!=None:
            self.text(p.interpolated[:,-1].tolist(),elabel,textargs='8 0 0 LB')
            

    def rsl_locations(self,rsldb,dataset=None, legend=None):
        """Plot RSL locations.

        rsldb: RSL database data set
        dataset: if not None, list of dataset ids to be plotted (when None, plot all)."""

        rsldata = rsldb.getLocationRange(self.file.minmax_long,self.file.minmax_lat)
        if legend != None:
            plot_locs = []
        for loc in rsldata:
            if legend != None:
                if loc[1] not in plot_locs:
                    plot_locs.append(loc[1])
                    ds = rsldb.getDataset(loc[1])
                    legend.plot_symbol(ds[1],CFcolours[loc[1]],'a')
                    
            self.geo.plotsymbol([loc[3]],[loc[4]],size=0.2,symbol='a',args='-G%s'%CFcolours[loc[1]])

    def rsl_res(self,rsldb):
        """Plot RSL residuals on map.

        rsldb: RSL database data set
        returns colourmap file"""

        # get data
        rsldata = rsldb.getLocationRange(self.file.minmax_long,self.file.minmax_lat)
        avgs = []
        mina =  10000.
        maxa = -10000.
        for loc in rsldata:
            xyloc = self.file.project([loc[3],loc[4]])
            if self.file.inside(xyloc):
                try:
                    a = self.file.get_rslres(rsldb,loc[0],avg=True)
                except:
                    continue
                if (mina>a): mina = a
                if (maxa<a): maxa = a
                avgs.append({'x': loc[3],'y':loc[4], 'a': a})

        # plot data
        for a in avgs:
            self.geo.plotsymbol([a['x']], [a['y']],size='%f 0.2'%a['a'],symbol='a',args='-C%s'%os.path.join(CFdatadir,'rsl_res.cpt'))
            

    def shapefile(self,fname,pen='2/0/0/0'):
        """Plot a shape file.

        fname: name of shape file
        pen: GMT pen attributes.

        This method uses the python interface to shapelib"""

        try:
            import shapelib
        except:
            print """Could not lot shapelib python module.

            You need to install the shapelib and the python wrapper to be able to plot
            shape files. Go and get it from here:
            http://shapelib.maptools.org/"""

            return

        shp = shapelib.ShapeFile(fname)
        (num_shapes,shp_type,shp_min,shp_max) = shp.info()

        # loop over shapes
        for i in range(0,num_shapes):
            obj = shp.read_object(i)
            posx = []
            posy = []
            # loop over vertices
            for j in range(0,len(obj.vertices()[0])):
                v = obj.vertices()[0][j]
                posx.append(v[0])
                posy.append(v[1])
            self.geo.line('-W%s'%pen,posx,posy)            
        

if __name__ == '__main__':
    from CF_options import *
    from CF_IOrsl import *
    
    parser = CFOptParser()
    parser.variable()
    parser.profile(vars=False)
    parser.time()
    parser.region()
    parser.plot()
    opts = CFOptions(parser,2)
    if opts.options.profname!=None:
        infile = opts.cfprofile()
    else:
        infile = opts.cffile()
    var = opts.vars(infile)
    ts = opts.times(infile)
    plot = opts.plot()
    area = CFArea(plot,infile)
    if opts.options.land:
        area.land(ts,illuminate=opts.options.illuminate)
    area.image(var,ts,clip = opts.options.clip,illuminate=opts.options.illuminate)
    area.coastline()
    if parser.profile!=None:
        area.profile(args='-W5/0/0/0')
    #rsl = CFRSL('/home/magi/Development/src/PyCF/pelt.dat')
    #area.rsl_locations(rsl)
    area.coordsystem()
    area.printinfo(ts)
    plot.close()
