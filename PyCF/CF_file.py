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

__all__ = ['CFfile']

from CF_proj import *

class CFfile(object):
    """The basic CF file class"""

    def __init__(self,fname):
        """Initialise.

        fname: name of CF file."""

        self.fname = fname
        self.file = None
        self.timescale = 0.001
        self.mapvarname = 'mapping'

        self.__projection = None
        self.__ll_xy_changed = False
        self.__ll_xy = [0,0]
        self.__ll_geo = [0,0]
        self.__ur_xy_changed = False
        self.__ur_xy = [0,0]
        self.__ur_geo = [0,0]
        
    # title
    def __set_title(self,title):
        setattr(self.file,'title',title)
    def __get_title(self):
        try:
            return getattr(self.file,'title')
        except:
            return self.fname
    title = property(__get_title,__set_title)

     # institution
    def __set_institution(self,institution):
        setattr(self.file,'institution',institution)
    def __get_institution(self):
        try:
            return getattr(self.file,'institution')
        except:
            return ''        
    institution = property(__get_institution,__set_institution)

    # source
    def __set_source(self,source):
        setattr(self.file,'source',source)
    def __get_source(self):
        try:
            return getattr(self.file,'source')
        except:
            return ''        
    source = property(__get_source,__set_source)

    # references
    def __set_references(self,references):
        setattr(self.file,'references',references)
    def __get_references(self):
        try:
            return getattr(self.file,'references')
        except:
            return ''        
    references = property(__get_references,__set_references)

    # comment
    def __set_comment(self,comment):
        setattr(self.file,'comment',comment)
    def __get_comment(self):
        try:
            return getattr(self.file,'comment')
        except:
            return ''        
    comment = property(__get_comment,__set_comment)

    # history
    def __set_history(self,history):
        setattr(self.file,'history',history)
    def __get_history(self):
        try:
            return getattr(self.file,'history')
        except:
            return ''        
    history = property(__get_history,__set_history)

    # lower left corner in projected coordinates
    def __get_ll_xy(self):
        return self.__ll_xy
    def __set_ll_xy(self,val):
        if self.inside(val):
            self.__ll_xy = val
            self.__ll_xy_changed = True
        else:
            raise RuntimeError, 'Point outside grid'
    ll_xy = property(__get_ll_xy,__set_ll_xy)
    # and geographic coordinates
    def __get_ll_geo(self):
        if self.__ll_xy_changed:
            self.__ll_geo = self.projection.proj4(self.__ll_xy,inv=True)
        return self.__ll_geo
    def __set_ll_geo(self,val):
        self.__set_ll_xy(self.projection.proj4(val))
        self.__ll_xy_changed = False
        self.__ll_geo = val
    ll_geo = property(__get_ll_geo,__set_ll_geo)

    #  upper right corner in projected coordinates
    def __get_ur_xy(self):
        return self.__ur_xy
    def __set_ur_xy(self,val):
        if self.inside(val):
            self.__ur_xy = val
            self.__ur_xy_changed = True
        else:
            raise RuntimeError, 'Point outside grid'
    ur_xy = property(__get_ur_xy,__set_ur_xy)
    # and geographic coordinates
    def __get_ur_geo(self):
        if self.__ur_xy_changed:
            self.__ur_geo = self.projection.proj4(self.__ur_xy,inv=True)
        return self.__ur_geo
    def __set_ur_geo(self,val):
        self.__set_ur_xy(self.projection.proj4(val))
        self.__ur_xy_changed = False
        self.__ur_geo = val
    ur_geo = property(__get_ur_geo,__set_ur_geo)
    
    # get projection info
    def __get_projection(self):
        if self.__projection == None:
            try:
                self.__projection = getCFProj(self.file.variables[self.mapvarname])
            except:
                raise RuntimeError, 'No projection selected yet'
        return self.__projection
    def __set_projection(self,proj):
        if self.mapvarname not in self.file.variables.keys():
            varmap=self.file.createVariable(self.mapvarname,'c',())
        copyCFMap(proj,varmap)
        self.__projection = getCFProj(proj)
        self.__ll_geo = self.projection.proj4(self.__ll_xy,inv=True)
        self.__ur_geo = self.projection.proj4(self.__ur_xy,inv=True)
    projection = property(__get_projection,__set_projection)

    def reset_bb(self):
        """Reset bounding box."""
        self.__ll_xy_changed = False
        self.__ll_xy = [self.file.variables['x1'][0],self.file.variables['y1'][0]]
        self.__ll_geo = self.projection.proj4(self.__ll_xy,inv=True)
        self.__ur_xy_changed = False
        self.__ur_xy = [self.file.variables['x1'][-1],self.file.variables['y1'][-1]]
        self.__ur_geo = self.projection.proj4(self.__ur_xy,inv=True)

    def close(self):
        """Close CF file."""
        self.file.close()
