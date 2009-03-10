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

"""Relative Sea Level Database.

This module provides I/O to the RSL database. I decided to use the python bindings
to SQLite because they provide a simple database which can be stored in a single
file which can be still be accessed from other languages. It should be no problem
to use a different SQL backend if that is needed since the Python DB API 2.0 is
used.
"""

__all__=['CFRSL']

import sqlite, optparse, sys, numpy, string

sqltables = [
    'CREATE TABLE author ('                         # author table
    'author_id INTEGER NOT NULL,'                   # unique id used for indexing
    'name VARCHAR(50) NOT NULL,'                    # name of author
    'first_name VARCHAR(50) NOT NULL,'              # first name of author
    'address VARCHAR(150), '                        # address of author
    'PRIMARY KEY (author_id))',
    
    'CREATE TABLE dataset ('                        # data set table
    'data_id INTEGER NOT NULL,'                     # unique id for data sets
    'name VARCHAR(50) NOT NULL,'                    # name of data set
    'source VARCHAR(100) NOT NULL,'                  # source of data set
    'PRIMARY KEY (data_id))',

    'CREATE TABLE dataset_author ('                 # this table is used to link authors with data sets
    'author_id INTEGER NOT NULL,'                   # unique id used for indexing
    'data_id INTEGER NOT NULL,'                     # unique id for data sets
    'FOREIGN KEY (author_id) REFERENCES author,'
    'FOREIGN KEY (data_id) REFERENCES dataset)',

    'CREATE TABLE location ('                       # this table holds location info
    'location_id INTEGER NOT NULL,'                 # unique id used for locations
    'data_id INTEGER NOT NULL,'                     # unique id for data sets
    'name VARCHAR(70) NOT NULL,'                    # first name of location
    'longitude REAL NOT NULL,'                      # longitude of location
    'latitude REAL NOT NULL,'                       # latitude of location
    'num INTEGER NOT NULL,'                         # number of measurements
    'PRIMARY KEY (location_id),'
    'FOREIGN KEY (data_id) REFERENCES dataset)',

    'CREATE TABLE measurement ('                    # this table holds all the measurements
    'measure_id INTEGER NOT NULL,'                  # unique id for each measurement
    'location_id INTEGER NOT NULL,'                 # unique id used for locations
    'time REAL NOT NULL,'                           # age of measurement
    'rsl REAL NOT NULL,'                            # measurement
    'time_p REAL, time_m REAL,'                     # age errors
    'rsl_p REAL, rsl_m REAL,'                       # measurement erros
    'PRIMARY KEY (measure_id),'
    'FOREIGN KEY (location_id) REFERENCES location)',

    # indices
    'CREATE INDEX index1 ON author (author_id)',
    'CREATE INDEX index2 ON dataset (data_id)',
    'CREATE INDEX index3 ON location (location_id)',
    'CREATE INDEX index4 ON location (longitude,latitude)',
    'CREATE INDEX index5 ON location (num)',
    'CREATE INDEX index6 ON measurement (measure_id)',
    'CREATE INDEX index7 ON measurement (location_id)'
    ]
    

class CFRSL(object):
    """The basic RSL class."""
    
    def __init__(self,name,create=False):
        """Initialise.

        name: name of database file
        create=False: set to True if you want to create tables, etc"""

        self.db = sqlite.connect(name)

        if create:
            cu = self.db.cursor()
            # creating tables
            for table in sqltables:
                cu.execute(table)
            self.db.commit()

        self.__mint = None
        self.__maxt = None

    def addAuthor(self,name,firstname,address):
        """Add an author.

        name: name of author
        firstname: first name of author
        address: address of author

        return new author_id"""

        cu = self.db.cursor()
        # get max id
        cu.execute('SELECT author_id FROM author')
        aid = len(cu.fetchall())
        #write data to db
        cu.execute('INSERT INTO author VALUES (%i, %s, %s, %s)',(aid,name,firstname,address))
        self.db.commit()
        return aid

    def addDataset(self,name,source,authors):
        """Add a data set.

        name: name of data set
        source: some source references
        authors: list of author ids.

        returns new dataset id."""

        cu = self.db.cursor()
        # see if authors are in database
        cu.execute('SELECT author_id FROM author')
        aid = cu.fetchall()
        for a in authors:
            if (a,) not in aid:
                raise LookupError, 'No author with id %d'%a
        
        # get max id
        cu.execute('SELECT data_id FROM dataset')
        did = len(cu.fetchall())
        #write data to db
        cu.execute('INSERT INTO dataset VALUES (%i, %s, %s)',(did,name,source))
        # link authors to data set
        for aid in authors:
            cu.execute('INSERT INTO dataset_author VALUES (%i, %i)',(aid,did))
        
        self.db.commit()
        return did

    def addLocation(self,name,longitude,latitude,dataset):
        """Add a new location.

        name: name of location
        lognitude: logitude of location
        latitude: latitude of location
        dataset: id of dataset the location belongs to

        returns new location id."""

        cu = self.db.cursor()
        # see if dataset is in database
        cu.execute('SELECT data_id FROM dataset WHERE data_id == %d',dataset)
        if (dataset,) not in cu.fetchall():
            raise LookupError, 'Dataset is not in database'

        # get max id
        cu.execute('SELECT location_id FROM location')
        lid = len(cu.fetchall())
        #write data to db
        cu.execute('INSERT INTO location VALUES (%i, %i, %s, %f, %f, 0)',(lid,dataset,name,longitude,latitude))
        self.db.commit()
        return lid

    def addMeasurements(self, location, time, rsl, time_error=None, rsl_error=None):
        """Add measurements to a location.
        
        location: id of a location
        time: array, list or tuple containing time measures
        rsl: array, list or tuple containing rsl measures
        time_error: when not None, [time_e+, time_e-]
                    where time_e+ and time_e- are either arrays, etc of length of time array, or a scalar
        rsl_error: when not None, [rsl_e+, rsl_e-], see description of time_error"""
        
        cu = self.db.cursor()
        # check if location is in db
        cu.execute('SELECT location_id FROM location WHERE location_id == %d',location)
        if (location,) not in cu.fetchall():
            raise LookupError, 'Location is not in database'

        # check length of data
        tel = False
        rel = False
        if len(time) != len(rsl):
            raise ValueError, 'Number of time measures is different from number of rsl measures.'
        if time_error!=None:
            if len(time_error) != 2:
                raise ValueError, 'Need positve and negative error bounds'
            if type(time_error[0]) in (list, tuple, numpy.ndarray):
                tel = True
                if (len(time_error[0]) != len(time) or len(time_error[1]) != len(time)):
                    raise ValueError, 'Time erros are not the same length as time measures.'
        if rsl_error!=None:
            if len(rsl_error) != 2:
                raise ValueError, 'Need positve and negative error bounds'
            if type(rsl_error[0]) in (list, tuple, numpy.ndarray):
                rel = True
                if (len(rsl_error[0]) != len(rsl) or len(rsl_error[1]) != len(rsl)):
                    raise ValueError, 'RSL erros are not the same length as rsl measures.'
             
        # get max id
        cu.execute('SELECT measure_id FROM measurement')
        mid = len(cu.fetchall())
        for i in range(0,len(time)):
            cu.execute('INSERT INTO measurement (measure_id, location_id, time, rsl) '
                       'VALUES (%i, %i, %f, %f)',(mid,location,time[i],rsl[i]))
            if time_error!=None:
                if tel:
                    error = [time_error[0][i],time_error[1][i]]
                else:
                    error = time_error
                cu.execute('UPDATE measurement SET time_p = %f, time_m = %f '
                           'WHERE measure_id == %i',(error[0],error[1],mid))
            if rsl_error!=None:
                if rel:
                    error = [rsl_error[0][i],rsl_error[1][i]]
                else:
                    error = rsl_error
                cu.execute('UPDATE measurement SET rsl_p = %f, rsl_m = %f '
                           'WHERE measure_id == %i',(error[0],error[1],mid))
            mid = mid + 1
        # increase the number of measures associated with location
        cu.execute('UPDATE location SET num = num+%i WHERE location_id == %i',(len(time),location))
        self.db.commit()

    def getLocationRange(self,longs,lats):
        """Get a range of locations.

        longs: [min,max] range of longitudes
        lats: [min,max] range of latitudes.

        returns an array of (id, long, lat, dataset)"""

        cu = self.db.cursor()
        cu.execute('SELECT * FROM location WHERE longitude BETWEEN %f AND %f AND latitude BETWEEN %f AND %f',
                   (float(longs[0]),float(longs[1]),float(lats[0]),float(lats[1])))
        
        return cu.fetchall()

    def getDataset(self,did):
        """Get dataset info.

        did: dataset id."""

        cu = self.db.cursor()
        cu.execute('SELECT * FROM dataset WHERE data_id == %i',(did))

        return cu.fetchone()

    def getLoc(self,lid):
        """Get location info.

        lid: location id."""

        cu = self.db.cursor()
        cu.execute('SELECT * FROM location WHERE location_id == %i',(lid))

        return cu.fetchone()

    def getRSLobs(self,lid):
        """Get RSL data set for single location.

        lid: location id."""

        cu = self.db.cursor()
        cu.execute('SELECT * FROM measurement WHERE location_id == %i',(lid))

        return cu.fetchall()

    def close(self):
        """Closing database."""

        self.db.close()

    def __LoadRSLminmaxT(self):
        """Find smallest and largest time observation."""

        if self.__mint == None or self.__maxt == None:
            cu = self.db.cursor()
            cu.execute('SELECT MIN(time), MAX(time) FROM measurement')
            tmp = cu.fetchall()
            self.__mint = tmp[0][0]
            self.__maxt = tmp[0][1]
            
    def __getRSLminT(self):
        """Get smallest time."""

        self.__LoadRSLminmaxT()
        return self.__mint
    mint = property(__getRSLminT)
    def __getRSLmaxT(self):
        """Get largest time."""

        self.__LoadRSLminmaxT()
        return self.__maxt
    maxt = property(__getRSLmaxT)    
    
# some private routines
def rsl_options():
    """generate options."""

    opts = optparse.OptionParser(usage="usage: %prog [options] database")

    opts.add_option("-l","--list",type="choice",choices=["author","dataset","location"],help="list available data, can be one of 'author','dataset','location'")
    opts.add_option("-a","--author",action="append",metavar="NAME FNAME EMAIL",type="string",nargs=3,help="add a new author, where NAME is the name, FNAME the first name and EMAIL, the email address of the author")
    opts.add_option("-d","--dataset",action="append",metavar="NAME SOURCE AUTHORS",type="string",nargs=3,help="add a new dataset, where NAME is the name and SOURCE is the source of the dataset. AUTHORS is a comma separated list of author ids.")
    opts.add_option("-p","--peltier",metavar="FNAME",type="string",help="add Peltier RSL database (ftp://ftp.ncdc.noaa.gov/pub/data/paleo/paleocean/relative_sea_level/sealevel.dat), FNAME is the name of the file containing the data.")
    opts.add_option("-o","--observation",metavar="ID",type="int",help="print data associated with location ID")
    
    opts.add_option("--create_db", default=False,action="store_true", help="create and initialise a new database")

    return opts

if __name__ == '__main__':

    opts = rsl_options()
    (options, args) = opts.parse_args()

    if len(args) != 1:
        print 'Need to specify which file to use.'
        sys.exit(1)

    try:
        rsl = CFRSL(args[0],create=options.create_db)
    except Exception,error:
        print error
        sys.exit(1)
        
    cursor = rsl.db.cursor()
    # listing entry
    if options.list != None:
        if options.list == 'author':
            cursor.execute('select * from author')
            author_list = cursor.fetchall()
            print '#id\tname\tfirst name\taddress'
            for a in author_list:
                print '%d\t%s\t%s\t%s'%(a[0],a[1],a[2],a[3])
        if options.list == 'dataset':
            cursor.execute('select * from dataset')
            dataset_list = cursor.fetchall()
            sys.stdout.write('#id\tname\tsource\tauthors\n')
            for d in dataset_list:
                sys.stdout.write('%d\t%s\t%s\t'%(d[0],d[1],d[2]))
                cursor.execute('select author.name from dataset_author,author '
                               'where data_id == %d and dataset_author.author_id == author.author_id',d[0])
                authors = cursor.fetchall()
                for a in authors:
                    sys.stdout.write('%s, '%(a[0]))
                print
        if options.list == 'location':
            cursor.execute('select * from location')
            location_list = cursor.fetchall()
            sys.stdout.write('#id\t\tlong\tlat\tnum\tname\n')
            for l in location_list:
                sys.stdout.write('%d\t%f\t%f\t%i\t%s\n'%(l[0],l[3],l[4],l[5],l[2]))
        sys.exit(0)

    if options.observation != None:
        loc = rsl.getLoc(options.observation)
        print 'id: %d\ndataset id: %d\nname: %s\ncoords: %f, %f\nnum obs:%d'%(loc[0],loc[1],loc[2],loc[3],loc[4],loc[5])
        print 'id\tlid\ttime\t\trsl\t\tterror\t\t\t\trerror'
        for i in rsl.getRSLobs(options.observation):
            print '%d\t%d\t%f\t%f\t(%f,%f)\t(%f,%f)'%(i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7])
        sys.exit(0)

    if options.author != None:
        for a in options.author:
            rsl.addAuthor(a[0],a[1],a[2])

    if options.dataset != None:
        for d in options.dataset:
            authors = []
            for a in d[2].split(','):
                authors.append(int(a))
            rsl.addDataset(d[0],d[1],authors)

    if options.peltier != None:
        # Add peltier data base
        aid1=rsl.addAuthor("Peltier","W.R.","Department of Physics\nUniversity of Toronto\nToronto, Ontario, Canada")
        aid2=rsl.addAuthor("Tushingham","A.M.","Geodynamics Section\nGeological Survey of Canada\nOttawa, Ontario, Canada")
        did =rsl.addDataset("Relative Sea Level Database","ftp://ftp.ncdc.noaa.gov/pub/data/paleo/paleocean/relative_sea_level/sealevel.dat",[aid1,aid2])
        df = open(options.peltier)
        n = -1
        for l in df.readlines():
            l = l.split()
            if n==-1:
                num = int(l[3])
                lid = rsl.addLocation(string.join(l[4:]),float(l[2]),float(l[1]),did)
                n = 0
                time = []
                rsl_data = []
                time_m = []
                time_p = []
                rsl_m = []
                rsl_p = []
            else:
                time.append(-float(l[0]))
                rsl_data.append(float(l[2]))
                time_m.append(-float(l[1]))
                time_p.append(float(l[1]))
                rsl_m.append(-float(l[3]))
                rsl_p.append(float(l[3]))
                n = n+1
                if n==num:
                    n=-1
                    rsl.addMeasurements(lid,time,rsl_data,[time_m,time_p],[rsl_m,rsl_p])

    rsl.close()
    

