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

"""Creating CF files."""

__all__=['CFVariableDef','CFcreatefile']

import Numeric, Scientific.IO.NetCDF,ConfigParser,os,re,string

class CFVariableDef(dict):
    """Dictionary containing variable definitions."""

    def __init__(self,filename):
        """Initialise Variable class.

        filename: name of file containing variable definitions."""

        dict.__init__(self)

        # reading variable configuration file
        vars = ConfigParser.ConfigParser()
        vars.readfp(open(filename))

        for v in vars.sections():
            vardef = {}
            vardef['name'] = v
            for (name, value) in vars.items(v):
                vardef[name] = value
            self.__setitem__(v,vardef)
            self.__add_spot(vardef)

    def __add_spot(self,vdef):
        """Add spot variable.

        vname: name of variable
        vdef:  variable definition"""

        if 'time' not in vdef['dimensions']:
            return

        spdef = {}
        for k in vdef:
            if k=='name':
                spdef[k] = '%s_spot'%vdef[k]
            elif k=='dimensions':
                search = re.search('y[0-1]\s*,\s*x[0-1]', vdef[k])
                if search!=None:
                    spdef[k] = vdef[k][:search.start()] + 'spot' + vdef[k][search.end():]
                else:
                    return
            else:
                spdef[k] = vdef[k]
        if 'x0' in vdef['dimensions']:
            spdef['coordinates'] = 'y0_spot x0_spot'
        else:
            spdef['coordinates'] = 'y1_spot x1_spot'
        self.__setitem__(spdef['name'],spdef)

    def keys(self):
        """Reorder standard keys alphabetically."""
        dk = []
        vk = []
        for v in dict.keys(self):
            if is_dimvar(self.__getitem__(v)):
                dk.append(v)
            else:
                vk.append(v)
        dk.sort()
        vk.sort()
        return dk+vk

class CFcreatefile(object):
    """Creating a CF netCDF file."""

    def __init__(self,fname):
        """Initialise.

        fname: name of CF file."""
        # get variable definitions
        try:
            vname=os.environ['GLIMMER_PREFIX']
        except KeyError:
            vname = os.path.expanduser(os.path.join('~','glimmer'))
        vname = os.path.join(vname,'share','glimmer','ncdf_vars.def')
        if not os.path.exists(vname):
            raise RuntimeError, 'Cannot find ncdf_vars.def\nPlease set GLIMMER_HOME to where glimmer is installed'
        self.vars = CFVariableDef(vname)
            
        self.file = Scientific.IO.NetCDF.NetCDFFile(fname,'w')
        self.file.Conventions = "CF-1.0"
        
    # title
    def __set_title(self,title):
        setattr(self.file,'title',title)
    def __get_title(self):
        return getattr(self.file,'title')
    title = property(__get_title,__set_title)

    # institution
    def __set_institution(self,institution):
        setattr(self.file,'institution',institution)
    def __get_institution(self):
        return getattr(self.file,'institution')
    institution = property(__get_institution,__set_institution)

    # source
    def __set_source(self,source):
        setattr(self.file,'source',source)
    def __get_source(self):
        return getattr(self.file,'source')
    source = property(__get_source,__set_source)

    # references
    def __set_references(self,references):
        setattr(self.file,'references',references)
    def __get_references(self):
        return getattr(self.file,'references')
    references = property(__get_references,__set_references)

    # comment
    def __set_comment(self,comment):
        setattr(self.file,'comment',comment)
    def __get_comment(self):
        return getattr(self.file,'comment')
    comment = property(__get_comment,__set_comment)

    # history
    def __set_history(self,history):
        setattr(self.file,'history',history)
    def __get_history(self):
        return getattr(self.file,'history')
    history = property(__get_history,__set_history)

    def createDimension(self,name, length):
        """Create a dimension.

        Creates a new dimension with the given name and length.
        length must be a positive integer or None, which stands for
        the unlimited dimension. Note that there can be only one
        unlimited dimension in a file."""
        self.file.createDimension(name,length)

    def close(self):
        """Close CF file."""
        self.file.close()

    def createVariable(self,name):
        """Create a CF variable.

        name: name of variable."""

        if name not in self.vars:
            raise KeyError, 'Cannot find definition for variable %s'%name
        v = self.vars[name]
        var = self.file.createVariable(name,Numeric.Float32,tuple(string.replace(v['dimensions'],' ','').split(',')))
        for a in ['long_name','standard_name','units']:
            if a in v:
                setattr(var,a,v[a])
        return var
