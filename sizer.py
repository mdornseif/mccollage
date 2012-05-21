#!/usr/bin/env python
# encoding: utf-8
"""
sizer.py - name a Minecraft World after it's size

Created by Maximillian Dornseif on 2012-05-18.
Copyright (c) 2012 Dr. Maximillian Dornseif. Consider it BSD Licensed.
"""

import sys
import subprocess
import os.path
import itertools, collections
import numpy
import math
from pymclevel import mclevel

import locale, os, sys
from struct import pack, unpack

from nbt.region import RegionFile
from nbt.chunk import Chunk
from nbt.world import AnvilWorldFolder,UnknownWorldFormat
 
def get_size(world_folder):
    # uses the nbt library which gives better results for anvil files
    world = AnvilWorldFolder(world_folder)  # Not supported for McRegion
    if not world.nonempty():  # likely still a McRegion file
        sys.stderr.write("World folder %r is empty or not an Anvil formatted world\n" % world_folder)
        return 65  # EX_DATAERR
    bb = world.get_boundingbox()
    return bb.lenx() * bb.lenz()


def main():
    for insert in sys.argv[1:]:
        if not os.path.isdir(insert):
            continue
        if not os.path.exists(os.path.join(insert, 'level.dat')):
            break
        siz = "%04d" % get_size(insert)
        base, end = os.path.split(insert)
        print siz, end
        newend = end[:]
        while len(newend) > 2 and (newend[0].isdigit() or newend[0] == '-'):
            newend = newend[1:]
        os.rename(os.path.join(base, end), os.path.join(base, "%s-%s" % (siz, newend)))
        
if __name__ == '__main__':
	main()

