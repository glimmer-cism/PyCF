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

"""Handling colourmaps."""

__all__=['CFcolourmap']

import os, PyGMT,Numeric

try:
    cname=os.environ['GLIMMER_PREFIX']
except:
    raise RuntimeError, 'Set GLIMMER_PREFIX to where glimmer is installed.'
cname = os.path.join(cname,'share','PyCF')
if not os.path.exists(cname):
            raise RuntimeError, 'Error, cannot find %s,\nPyCF is not installed properly.'%cname

class CFcolourmap(object):
    """Colourmaps."""

    STDN_MAP = { 'bedrock_altitude' : 'topo.cpt',
                 'land_ice_thickness' : 'ice.cpt',
                 'land_ice_surface_mass_balance' : 'mb.cpt',
                 'land_ice_basal_melt_rate' : 'mb.cpt',
                 'land_ice_basal_x_velocity' : 'velo.cpt',
                 'land_ice_basal_y_velocity' : 'velo.cpt',
                 'surface_temperature' : 'temp.cpt',
                 'lwe_precipitation_rate' : 'mb.cpt',
                 'land_ice_x_velocity' : 'velo.cpt',
                 'land_ice_y_velocity' : 'velo.cpt',
                 'land_ice_temperature' : 'temp.cpt'}
    VARN_MAP = { 'relx' : 'topo.cpt',
                 'presprcp' : 'mb.cpt',
                 'presusrf' : 'ice.cpt',
                 'ubas' : 'velo.cpt',
                 'vbas' : 'velo.cpt',
                 'thk' : 'ice.cpt',
                 'usurf' : 'ice.cpt',
                 'lsurf' : 'topo.cpt',
                 'topg' : 'topo.cpt',
                 'acab' : 'mb.cpt',
                 'bmlt' : 'mb.cpt',
                 'artm' : 'temp.cpt',
                 'btemp' : 'temp.cpt',
                 'prcp' : 'mb.cpt',
                 'ablt' : 'mb.cpt',
                 'uvel' : 'velo.cpt',
                 'vvel' : 'velo.cpt',
                 'wvel' : 'velo.cpt',
                 'temp' : 'temp.cpt'}

    def __init__(self,var,filename=None):
        """Initialise.

        var: CF variable
        filename : name of GMT CPT file, if None, do all the automagic."""

        self.var = var
        self.name = var.name
        self.long_name = var.long_name
        self.units = var.units

        if filename != None:
            self.__cptfile = filename
        else:
            self.__cptfile = None
            if self.name in self.VARN_MAP:
                self.__cptfile = os.path.join(cname,self.VARN_MAP[self.name])
            elif var.standard_name in self.STDN_MAP:
                self.__cptfile = os.path.join(cname,self.STDN_MAP[var.standard_name])
            else:
                self.__cptfile = '.__auto.cpt'
                
    def __get_cptfile(self):
        if self.__cptfile == '.__auto.cpt':
            v0 = min(Numeric.ravel(self.var.file.variables[self.name]))
            v1 = max(Numeric.ravel(self.var.file.variables[self.name]))
            PyGMT.command('makecpt','-Crainbow -T%f/%f/%f > .__auto.cpt'%(v0,v1,(v1-v0)/10.))
        return self.__cptfile
    cptfile = property(__get_cptfile)
            
    def __get_title(self):
        title = self.long_name
        if len(self.units)>0 and len(self.units)>0:
            title = title + ' '
        if len(self.units)>0:
            title = title + '[%s]'%self.units
        return title
    title = property(__get_title)
        
        
