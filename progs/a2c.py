#! /usr/bin/env python

# Copyright Stewart Jamieson (Stewart.Jamieson@ed.ac.uk) and Magnus Hagdorn, 2005 - University of Edinburgh.
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

# This script reads a single ascii spatial data file (e.g. created in ArcGIS) and outputs a netCDF file.

import sys, getopt,Numeric, PyCF, datetime, string, PyCF.CF_proj

def usage():
    "print short help message"

    print 'Usage: a2c.py [OPTIONS] infile outfile'
    print 'create a radial CF topography file based on Sine wave.'
    print 'infile = input ascii file e.g. input.asc'
    print 'outfile = output netCDF file e.g. output.nc'
    print ''
    print '  -h, --help\n\tthis message'
    print '  -p, --projection\n\tname of projection file'
    print '  -e, --extras\n\tname of text file containing space delimited list of\n\textra variables and associated ascii filenames'
    print '  -v, --variable\n\talternative name for input variable [default topg]'
    print '  --title\n\ttitle for output netCDF file'
    print '  --institution\n\tname of institution'
    print '  --references\n\tsome references'
    print '  --comment\n\tcomment'

# get options
try:
    opts, args = getopt.getopt(sys.argv[1:],'hp:e:v:',['help','projection=','extras=','variable=','title=','institution=','references=','comment='])
except getopt.GetoptError,error:
        # print usage and exit
        print error
        usage()
        sys.exit(1)
        
if len(args) == 2:
        inFile = args[0]
        outFile = args[1]
else:
        usage()
        sys.exit(1)


title='Ascii Topo'
institution=None
references=None
comment=None
proj = None
upper = None
source=None
inProjFile=None
extraFile=None
variable='topg'
varname='var'+ variable
origin = None
delta = None
num = None
for o,a in opts:
    if o in ('-h', '--help'):
        usage()
        sys.exit(0)
    if o in ('-p', '--projection'):
    	inProjFile = a
    if o in ('-e','--extras'):
    	extraFile = a
    if o in ('-v','--variable'):
    	variable = a
    	varname = 'var' + variable
    if o == '--title':
        title = a
    if o == '--institution':
        institution = a
    if o == '--references':
        references = a
    if o == '--comment':
        comment  = a


f=open(inFile, 'r')

#read first few lines to get metadata
numx=f.readline()
numx=int(numx[14:])

numy=f.readline()
numy=int(numy[14:])

xll=f.readline()
xll=float(xll[14:])

yll=f.readline()
yll=float(yll[14:])

res=f.readline()
res=float(res[14:])

nd=f.readline()
nd=float(nd[14:])


# Deal with projection information

if inProjFile == None:
  proj = None
else:
  print 'Parsing projection...'
  pFile=open(inProjFile, 'r')
  proj = PyCF.CF_proj.CFProj_parse_ESRIprj(pFile)

  
origin = [float(xll),float(yll)]
delta = [float(res),float(res)]

print 'creating output netCDF file...'
cffile = PyCF.CFcreatefile(outFile)
# global attributes
if title is not None:
    cffile.title = title
if institution is not None:
    cffile.institution = institution
if source  is not None:
    cffile.source = source
args = ''
for a in sys.argv:
    args = args + '%s '%a
cffile.history = '%s: %s'%(datetime.datetime.today(),args)
if references  is not None:
    cffile.references=references
if comment is not None:
    cffile.comment = comment

# creating dimensions
cffile.createDimension('x0',numx-1)
cffile.createDimension('x1',numx)
cffile.createDimension('y0',numy-1)
cffile.createDimension('y1',numy)
cffile.createDimension('level',1)
cffile.createDimension('time',None)
# creating variables
varx=cffile.createVariable('x0')
varx[:] = ((delta[0]*Numeric.arange(numx-1)+(delta[0]/2))+origin[0]).astype(Numeric.Float32)
varx=cffile.createVariable('x1')
varx[:] = ((delta[0]*Numeric.arange(numx))+origin[0]).astype(Numeric.Float32)
varlist=['varx'] #store information about which variables have already been created

vary=cffile.createVariable('y0')
vary[:] = ((delta[1]*Numeric.arange(numy-1)+(delta[1]/2))+origin[1]).astype(Numeric.Float32)
vary=cffile.createVariable('y1')
vary[:] = ((delta[1]*Numeric.arange(numy))+origin[1]).astype(Numeric.Float32)
varlist.append('vary')

varlevel=cffile.createVariable('level')
varlevel[0] = 1
varlist.append('level')

vartime=cffile.createVariable('time')
vartime[0] = 0
varlist.append('time')

if proj is not None:
    cffile.projection=proj

varlat=cffile.createVariable('lat')
varlist.append('lat')
varlong=cffile.createVariable('lon')
varlist.append('lon')
varname=cffile.createVariable(variable)
varlist.append(variable)


# get long/lat
longs = varlong[0,:,:]
lats = varlat[0,:,:]
for i in range(0,numy):
    longs[i,:] = varx[:]
for i in range(0,numx):
    lats[:,i] = vary[:]

lats.shape = (numx*numy,)
longs.shape = (numx*numy,)
if inProjFile != None:
	print 'Projecting file...'
	(longs,lats) = cffile.projection.Proj4.gridinv((longs,lats)) # uses the projection method of cffile to project the file.


lats.shape = (numy,numx)
longs.shape = (numy,numx)
varlong[0,:,:] = longs[:,:].astype(Numeric.Float32)
varlat[0,:,:] = lats[:,:].astype(Numeric.Float32)


#define array for the zData
zData=Numeric.zeros((numx,numy),Numeric.Float32)

j=numy-1
for l in f.readlines():
    i=0
    for e in l.split():
	# insert each value into each array element
	e=float(e) 
	zData[i,j]=e
	i=i+1
    j=j-1

varname[0,:,:] =  Numeric.transpose(zData[:,:]).astype(Numeric.Float32)

# open file containing list of extra variables and their associated inputs
if extraFile != None:
  extra=open(extraFile, 'r')
  # loop here for variables listed in extraFile
  line = extra.readline()
  while line != '':
	l = line.split()
	#print 'line = ',l
	variable = l[0]
	#if variable already exists in varlist then ignore new variable and skip to next line
	#else parse as normal and add variable to varlist
	
	
	print 'Parsing variable',variable,'...'
	dataFile = open(l[1], 'r')
	
	#skip metadata
	xsize=dataFile.readline()
	xsize=int(xsize[14:])
	if xsize != numx:
		print 'Error in input file',l[1],'Check X dimension of all files is same as file',inFile
		sys.exit(1)
	ysize=dataFile.readline()
	ysize=int(ysize[14:])
	if ysize != numx:
		print 'Error in input file',l[1],'Check Y dimension of all files is same as file',inFile
		sys.exit(1)
	skip=dataFile.readline()
	skip=dataFile.readline()
	skip=dataFile.readline()
	skip=dataFile.readline()

	#define array for the zData
	zData=Numeric.zeros((numx,numy),Numeric.Float32)

	j=numy-1
	for l in dataFile.readlines():
    		i=0
    		for e in l.split():
			# insert each value into each array element
			e=float(e) 
			zData[i,j]=e
			i=i+1
    		j=j-1

	varname = 'var' + variable
	varname=cffile.createVariable(variable)
	varlist.append(variable)
	varname[0,:,:] =  Numeric.transpose(zData[:,:]).astype(Numeric.Float32)
	line = extra.readline()
  else:
    print ' '
  #finish loop for extraFile here

print 'NetCDF file',outFile,'created'

cffile.close()
