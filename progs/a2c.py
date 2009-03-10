#! /usr/bin/env python

# Stewart Jamieson (Stewart.Jamieson@ed.ac.uk) and Magnus Hagdorn, 2005 - University of Edinburgh.
# This script reads ascii spatial data files (e.g. created in ArcGIS) and outputs a netCDF file.

import sys, getopt,numpy, PyCF, datetime, string, PyCF.CF_proj

def usage():
    "print short help message"

    print 'Usage: a2c.py [OPTIONS] infile outfile'
    print 'Converts ArcInfo/ArcMap ascii files to netCDF format.'
    print 'infile = input ascii file e.g. input.asc'
    print 'outfile = output netCDF file e.g. output.nc'
    print ''
    print '  -h, --help\n\tthis message'
    print '  -p, --projection\n\tname of projection file'
    print '  -e, --extras\n\tname of text file containing space delimited list of\n\textra variables, associated ascii filenames,\n\tconversion (multiplication) factor and a nodata alternative.\n\tyou must always give a conversion factor\n\t- just use 1 if you do not wish to convert.'
    print '  -v, --variable\n\talternative name for input variable [default topg]'
    print '  -n, --nodata\n\tthe value you wish any NODATA value to become'
    print '  -c, --conversion\n\ta multiplication factor should you need to scale the default variable data'
    print '  -s, --shift\n\ta shift factor to increase or decrease the default variable'
    print '  -a, --add\n\tadd an extra variable that has a constant value [e.g. varname/value]'
    print '  --title\n\ttitle for output netCDF file'
    print '  --institution\n\tname of institution'
    print '  --references\n\tsome references'
    print '  --comment\n\tcomment'

# get options
try:
    opts, args = getopt.getopt(sys.argv[1:],'hp:e:v:n:c:s:a:',['help','projection=','extras=','variable=','nodata=','conversion=','shift=','add=','title=','institution=','references=','comment='])
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
coversion_factor = 1.0
conv_factor = 1.0
nodata_val = 1
shift = 0.0
add = None
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
    if o in ('-n','--nodata'):
    	nodata_val = a
    if o in ('-c','--conversion'):
    	conv_factor = a
    if o in ('-s','--shift'):
    	shift = float(a)
    if o in ('-a','--add'):
    	a = a.split('/')
    	try:
	  add = [a[0],a[1]]
	except:
	  print 'Error, cannot parse num string'
	  usage()
          sys.exit(1)
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
numx=int(numx[string.rfind(numx,' '):])

numy=f.readline()
numy=int(numy[string.rfind(numy,' '):])

xll=f.readline()
xll=float(xll[string.rfind(xll,' '):])

yll=f.readline()
yll=float(yll[string.rfind(yll,' '):])

res=f.readline()
res=float(res[string.rfind(res,' '):])

nd=f.readline()
nd=float(nd[string.rfind(nd,' '):])

def DmsParse(pFile): 
	# This parses a string from the projection file
	l = string.split(pFile.readline())
	deg = float(l[0])
	min = float(l[1])/60
	sec = float(l[2])/3600
	dms=(deg)+(min)+(sec)
    	return dms


# Deal with projection information

if inProjFile == None:
  proj = None
else:
  print 'Parsing projection...'
  pFile=open(inProjFile, 'r')
  pName = pFile.readline()
  pName=pName[14:]
  
  pStrip = string.strip(pName)
  print pStrip
  proj = PyCF.CF_proj.DummyProj()
  
  if pStrip == 'ALBERS':
      proj.grid_mapping_name='albers_conical_equal_area'
      line = pFile.readline()
      while line != '':
      	  line = pFile.readline()
          if string.strip(line) == 'Parameters':
    		  standard1=DmsParse(pFile)
    		  standard2=DmsParse(pFile)
    		  proj.standard_parallel = [standard1,standard2]
    		  long_central=DmsParse(pFile)
    		  if long_central < 0:
    			  long_central = 360+long_central
    			  proj.longitude_of_central_meridian = [long_central]
    		  else:
    			  proj.longitude_of_central_meridian = [long_central]
    		  lat_proj_origin=DmsParse(pFile)
    		  proj.latitude_of_projection_origin = [lat_proj_origin] 
    		  east=pFile.readline()
    		  east=string.strip(east)
    		  east_index = string.index( east, ' /* false easting (meters)', 0, 100) 
    		  east=east[:east_index]
    		  proj.false_easting=string.atof(east)
    		  north=pFile.readline()
                  north=string.strip(north)
		  north_index = string.index( north, ' /* false northing (meters)', 0, 100) 
		  north=north[:north_index]
    		  proj.false_northing=string.atof(north)

  
  elif pStrip == 'LAMBERT':
      proj.grid_mapping_name='lambert_conformal_conic'
      line = pFile.readline()
      while line != '':
          line = pFile.readline()
          if string.strip(line) == 'Parameters':
    		  standard1=DmsParse(pFile)
    		  standard2=DmsParse(pFile)
    		  proj.standard_parallel = [standard1,standard2]
    		  long_central=DmsParse(pFile)
		  if long_central < 0:
			  long_central = 360+long_central
			  proj.longitude_of_central_meridian = [long_central]
		  else:
			  proj.longitude_of_central_meridian = [long_central]
    		  lat_proj_origin=DmsParse(pFile)
    		  proj.latitude_of_projection_origin = [lat_proj_origin]
    		  east=pFile.readline()
    		  east=string.strip(east)
    		  east_index = string.index( east, ' /* false easting (meters)', 0, 100) 
    		  east=east[:east_index]
    		  proj.false_easting=string.atof(east)
    		  north=pFile.readline()
                  north=string.strip(north)
		  north_index = string.index( north, ' /* false northing (meters)', 0, 100) 
		  north=north[:north_index]
    		  proj.false_northing=string.atof(north)

  
  elif pStrip == 'LAMBERT_AZIMUTHAL':
      proj.grid_mapping_name='lambert_azimuthal_equal_area'
      line = pFile.readline()
      while line != '':
          line = pFile.readline()
          if line != '':
          	first = string.split(line)
          	if first[0] == 'Parameters':
                  	skip = pFile.readline() #skip a line as data not required
    		  	long_central=DmsParse(pFile)
		  	if long_central < 0:
			  	long_central = 360+long_central
			  	proj.longitude_of_central_meridian = [long_central]
		  	else:
			  	proj.longitude_of_central_meridian = [long_central]
    		  	lat_proj_origin=DmsParse(pFile)
    		  	proj.latitude_of_projection_origin = [lat_proj_origin]
    		  	east=pFile.readline()
			east=string.strip(east)
			east_index = string.index( east, ' /* false easting (meters)', 0, 100) 
			east=east[:east_index]
			proj.false_easting=string.atof(east)
			north=pFile.readline()
			north=string.strip(north)
			north_index = string.index( north, ' /* false northing (meters)', 0, 100) 
			north=north[:north_index]
			proj.false_northing=string.atof(north)



  # Due to inconsistencies between ESRI projection files and the parameters required by CFProj, the stereographic
  # projections may produce incorrect results so CHECK them carefully!. 
  elif pStrip == 'STEREOGRAPHIC':
      
      line = pFile.readline()
      while line != '':
          line = pFile.readline()
          if line != '':
            first = string.split(line)
            if first[0] == 'Parameters':

              l = string.split(pFile.readline())
              type = l[0]
              if type == '2':
                  flag = 0
                  if flag == 0:
                  	long_central=DmsParse(pFile)
                  	lat_proj_origin=DmsParse(pFile)
                  	proj.latitude_of_projection_origin = [lat_proj_origin]
                  	pol_v_eq = string.split(pFile.readline()) # get whether a polar or equatorial view.
                  	pol_v_eq = pol_v_eq[0]
                  	proj.false_easting=0
                      	proj.false_northing=0
                  	flag = 1
                  	
                  if flag == 1:
                  	if pol_v_eq == 'EQUATORIAL':
                      		proj.grid_mapping_name='stereographic' # type 2 stereographic projection with equatorial
                      		proj.longitude_of_central_meridian = [long_central] # long of cent projection
                      		l = string.split(pFile.readline())
                      		scale_factor=l[0]
                      		proj.scale_factor_at_projection_origin = [scale_factor] # scale factor
                  	else:
                      		proj.grid_mapping_name='polar_stereographic' # type 2 stereographic projection with north or southpole
                      		proj.straight_vertical_longitude_from_pole = [long_central] 
                      		#l = string.split(pFile.readline())
                      		#lat_std_par = int(float(l[0]))
                      		lat_std_par = DmsParse(pFile)
                      		proj.standard_parallel = [lat_std_par] # lat of standard parallel
                      		
              
              elif type == '1':
                  proj.grid_mapping_name='stereographic'
                  line=pFile.readline()
                  long_central=DmsParse(pFile)
                  proj.longitude_of_central_meridian = [long_central]
                  lat_proj_origin=DmsParse(pFile)
                  proj.latitude_of_projection_origin = [lat_proj_origin]
                  scale_factor=1. #defaults to 1 as Arc projection files do not include scale factors
                  proj.scale_factor_at_projection_origin = [scale_factor]
                  
                  east=pFile.readline()
		  east=string.strip(east)
		  east_index = string.index( east, ' /* false easting (meters)', 0, 100) 
		  east=east[:east_index]
		  proj.false_easting=string.atof(east)
		  north=pFile.readline()
		  north=string.strip(north)
		  north_index = string.index( north, ' /* false northing (meters)', 0, 100) 
		  north=north[:north_index]
    		  proj.false_northing=string.atof(north)
                  
                  #false_easting=string.split(string.strip(pFile.readline()))
                  #false_easting=false_easting[0]
                  #proj.false_easting=0
                  #false_northing=string.split(string.strip(pFile.readline()))
                  #false_northing=false_northing[0]
                  #proj.false_northing=0
    
  else:
      print 'Projection ',pStrip,' not recognized'
      print 'This program will only recognise albers equal area, lambert, lambert azimuthal and stereographic projections.'
      sys.exit(1)


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
varx[:] = ((delta[0]*numpy.arange(numx-1)+(delta[0]/2))+origin[0]).astype('f')
#varx[:] = (delta[0]*numpy.arange(numx-1)).astype('f')
varx=cffile.createVariable('x1')
varx[:] = ((delta[0]*numpy.arange(numx))+origin[0]).astype('f')
varlist=['varx'] #store information about which variables have already been created

vary=cffile.createVariable('y0')
vary[:] = ((delta[1]*numpy.arange(numy-1)+(delta[1]/2))+origin[1]).astype('f')
#vary[:] = (delta[1]*numpy.arange(numy-1)).astype('f')
vary=cffile.createVariable('y1')
vary[:] = ((delta[1]*numpy.arange(numy))+origin[1]).astype('f')
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
varlong[0,:,:] = longs[:,:].astype('f')
varlat[0,:,:] = lats[:,:].astype('f')


#define array for the zData
zData=numpy.zeros((numx,numy),'f')

j=numy-1
for l in f.readlines():
    i=0
    for e in l.split():
	# insert each value into each array element
	e=float(e)
	if e == nd: e = float(nodata_val)
	zData[i,j]=e*float(conv_factor)+shift
	i=i+1
    j=j-1

varname[0,:,:] =  numpy.transpose(zData[:,:]).astype('f')


#add in any variables that are supposed to show constant values.
if add != None:
    addvar = str(add[0])
    addval = float(add[1])
    print addvar
    print addval
    varnew=cffile.createVariable(addvar)
    varlist.append(addvar)
    
    if addvar != 'eus':
       zData=numpy.zeros((numx,numy),'f')
       for n in range(0,numy):
     	  zData[n,:] = addval
       for n in range(0,numx):
     	  zData[:,n] = addval
       varnew[0,:,:] =  numpy.transpose(zData[:,:]).astype('f')
    
    #eus (sea level change) is a cingle dimension variable, so we only assign a shift in sea level to the cffile.
    if addvar == 'eus':
       varnew[0] = addval

# open file containing list of extra variables and their associated inputs
if extraFile != None:
  extra=open(extraFile, 'r')
  # loop here for variables listed in extraFile
  line = extra.readline()
  #print 'line',line,'line'
  while line != '':
	l = line.split()
	#print 'line = ',l
	variable = l[0]
	#if variable already exists in varlist then ignore new variable and skip to next line
	#else parse as normal and add variable to varlist
	
	
	print 'Parsing variable',variable,'...'
	dataFile = open(l[1], 'r')
	
	if len(l) > 2: conversion_factor = float(l[2])
	
	if len(l) > 3: nodata_val = float(l[3])
	
	#skip metadata
	xsize=dataFile.readline()
	xsize=int(xsize[string.rfind(xsize,' '):])
	if xsize != numx:
		print 'Error in input file',l[1],'Check X dimension of all files is same as file',inFile
		sys.exit(1)
	ysize=dataFile.readline()
	ysize=int(ysize[string.rfind(ysize,' '):])
	if ysize != numy:
		print 'Error in input file',l[1],'Check Y dimension of all files is same as file',inFile
		sys.exit(1)
	skip=dataFile.readline()
	skip=dataFile.readline()
	skip=dataFile.readline()
	skip=dataFile.readline()

	#define array for the zData
	zData=numpy.zeros((numx,numy),'f')

	j=numy-1
	for l in dataFile.readlines():
    		i=0
    		for e in l.split():
			# insert each value into each array element
			e=float(e)
			if e == nd: 
			  e = float(nodata_val)
			  zData[i,j]=e
			else:
			  zData[i,j]=e*conversion_factor
			i=i+1
    		j=j-1

	varname = 'var' + variable
	varname=cffile.createVariable(variable)
	varlist.append(variable)
	varname[0,:,:] =  numpy.transpose(zData[:,:]).astype('f')
	line = extra.readline()
  else:
    print 'all variables parsed'
  #finish loop for extraFile here

print 'NetCDF file',outFile,'created'

cffile.close()
