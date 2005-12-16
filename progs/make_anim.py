#! /usr/bin/env python

"""Create a funky animation."""

import sys, tempfile, os.path, string, os,shutil 
from optparse import OptionParser

CODECS = "mjpeg mpeg4 msmpeg4 msmpeg4v2 wmv1 wmv2 rv10 asv1 asv2"

parser = OptionParser(usage="%prog [options] plotting_command",description="Create a funky animation using mencoder and ImageMagic")
parser.add_option("-b", "--brand", default=False, action="store_true", help="add branding")
parser.add_option("-f", "--fps", default=25,  type="int", metavar = "FPS", help="set frames per second to FPS (default: 25)")
parser.add_option("-c", "--codec",metavar='CODEC',type="choice",choices=CODECS.split(), default="wmv2", help="select codec where CODEC is one of: %s (default: wmv2)"%CODECS)
parser.add_option("-s", "--size", metavar = "SIZE", help="scale animation to SIZE, use convert options for specifying size")
parser.add_option("-t", "--time", metavar = "S E", nargs=2, type="int", help="start and end time")
parser.add_option("-o", "--output", default="anim.avi", metavar="FILE", help="write output to FILE (default: anim.avi)")
parser.add_option("--convert_options",default="",help="options for convert")

(options, args) = parser.parse_args()

if options.time == None:
    parser.error('no time interval given')
if len(args) == 0:
    parser.error('no plotting command given')

size = ''

# create a temporary directory where all the frames are stored
frame_dir = tempfile.mkdtemp('-anim')

for t in range(options.time[0],options.time[1]):
    psfile  = '%s.%06d.ps'%(os.path.join(frame_dir,'tmp'),t)
    pngfile = '%s.%06d.png'%(os.path.join(frame_dir,'tmp'),t)
    plot_command = '%s %s -T%d'%(string.join(args),psfile,t)
    if options.size!=None:
        convert_command = 'convert %s -trim -size %s %s -resize %s %s'%(options.convert_options,options.size,psfile,options.size,pngfile)
    else:
        convert_command = 'convert -trim %s %s'%(psfile,pngfile)
    
    os.system(plot_command)
    os.system(convert_command)
    os.remove(psfile)


encode_command = 'mencoder mf://%s/*.png -mf fps=%d:type=png -ovc lavc -lavcopts vcodec=%s -o %s'%(frame_dir,options.fps,options.codec,options.output)
os.system(encode_command)

# cleaning up
shutil.rmtree(frame_dir)
