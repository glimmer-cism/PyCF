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

"""Plot EISMINT-2 statistics."""

import PyGMT,PyCF,sys,os

single = ['A','G','H']
CFstat_names_GMT = ['Volume','Area','Melt fraction','Divide thickness','Divide basal temp']
CFstat_units = {'single':[' [10@+6@+km@+3@+]',' [10@+6@+km@+2@+]','',' [m]',' [\\353C]'], 'comp':[' [%]',' [%]',' [%]',' [%]',' [\\353C]']}

def parse_eis2file(name):
    """Parse the eismint2 data file

    name: name of file containing EISMINT2 data"""
    

    eis2file = open(name)

    eis2data = {}
    for line in eis2file.readlines():
        line = line.strip()
        if len(line)==0:
            continue
        if line[0] == '#':
            continue
        elif line[0] == '[':
            exp = {}
            end = line.find(']')
            exp_name = line[1:end]
            eis2data[exp_name]=exp
            continue
        else:
            data = []
            line = line.split()
            for i in range(1,len(line)):
                if i==5 and exp_name in single:
                        data.append(float(line[i])-273.15)
                else:
                    data.append(float(line[i]))
            exp[line[0]] = data
    eis2file.close()
    return eis2data

class EIS2plot(PyGMT.AutoXY):
    """Plot EISMINT-2 statistics"""

    def __init__(self,parent,pos=[0.,0.],size=[6.,6.]):
        """Initialising GMT area.

        parent: can be either a Canvas or another Area.
        pos: position of area relative to the parent
        size: size of GMT area
        """

        # initialising data
        PyGMT.AutoXY.__init__(self,parent,pos=pos,size=size)
        self.__keys = None
        self.axis='Wesn'
        self.xtic='1'
        self.__num = 0

    def plot_paper(self,eis2data,statnum):
        """Plot results of EISMINT 2 paper.

        eis2data: directory holding EISMINT2 results
        statnum: id of statistic to be plotted"""

        # plotting bar graphs
        self.__keys = eis2data.keys()
        self.__keys.sort()

        for i in range(0,len(self.__keys)):
            self.plotsymbol([i],[eis2data[self.__keys[i]][statnum]],size="",symbol='b1u',args='-G125 -W1/255')
        self.__num = self.__num + i + 1

    def plot(self,data,colour):
        """Plot experiment.

        data: data value
        colour: colour for bar."""

        self.plotsymbol([self.__num],[data],size="",symbol='b1u',args='-G%s -W1/255'%colour)
        self.__num = self.__num + 1

    def finalise(self):
        """Finalise plot."""

        self.ll[0] = self.ll[0]-0.5
        self.ur[0] = self.ur[0]+0.5
        PyGMT.AutoXY.finalise(self,expandy=True)

    def coordsystem(self):
        """Plot coordinate system"""

        PyGMT.AutoXY.coordsystem(self)
        tarea = PyGMT.AreaXY(self,size=self.size,pos=[0,-0.5])
        tarea.setregion([self.ll[0],0],[self.ur[0],1.])
        for i in range(0,len(self.__keys)):
            tarea.text([i,0],self.__keys[i],textargs='10 0 0 CB',comargs="")

if __name__ == '__main__':
        
    eis2data = parse_eis2file(os.path.join(PyCF.CFdatadir,'eismint2.data'))
    parser = PyCF.CFOptParser("""usage: %prog [options] infile1 [infile2 ... infileN]
    plots statistics of EISMINT-2 experiments.""")
    parser.add_option("-e","--experiment",default="A",metavar="EXP",type="choice",choices=['A','B','C','D','G','H'],help="select EISMINT-2 experiment to be plotted. If one of ['B','C','D'] is selected you need to give pairs of input files containing the experiment and the exp A to be compared to.")

    opts = PyCF.CFOptions(parser,-2)
    

    exp=opts.options.experiment

    plot = opts.plot()
    plot.defaults['LABEL_FONT_SIZE']='12p'
    plot.defaults['ANNOT_FONT_SIZE']='10p'
    bigarea = PyGMT.AreaXY(plot,size=[30,30],pos=[0,0])

    if exp in single:
        increment = 1
        unit='single'
        # title
        bigarea.text([7.5,22],'Experiment %s'%exp,textargs='18 0 0 CM')
    else:
        increment = 2
        unit='comp'
        # title
        bigarea.text([7.5,22],'Differences between Experiment %s and A'%exp,textargs='18 0 0 CM')

    # setting up plots
    plots = []
    plots.append(EIS2plot(bigarea,pos=[0,15]))
    plots.append(EIS2plot(bigarea,pos=[9,15]))
    plots.append(EIS2plot(bigarea,pos=[0,7.5]))
    plots.append(EIS2plot(bigarea,pos=[9,7.5]))
    plots.append(EIS2plot(bigarea,pos=[0,0]))
    key = PyGMT.KeyArea(bigarea,pos=[7,0],size=[10.,6.])
    key.num = [2,10]

    for i in range(0,len(plots)):
        plots[i].plot_paper(eis2data[exp],i)
        plots[i].ylabel = '%s%s'%(CFstat_names_GMT[i],CFstat_units[unit][i])

    for f in range(0,opts.nfiles,increment):
        cffile = opts.cffile(f)
        key.plot_box(cffile.title,PyCF.CFcolours[f])
        if increment == 1:
            eis = PyCF.CFgetstats(cffile,-1,eismint=True)
        else:
            compfile = opts.cffile(f+1)
            comp = PyCF.CFgetstats(compfile,-1,eismint=True)
            eis = PyCF.CFgetstats(cffile,-1,eismint=True)
            eis = eis - comp
            for i in range(0,4):
                eis[i]=100.*eis[i]/abs(comp[i])
        for i in range(0,len(plots)):
            plots[i].plot(eis[i],PyCF.CFcolours[f])

    # finialising plots
    for i in range(0,len(plots)):
        plots[i].finalise()
        plots[i].coordsystem()
    
    plot.close()
