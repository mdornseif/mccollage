#!/usr/bin/env python
# encoding: utf-8
"""
border.py - merge a Minecraft World into an other

Created by Maximillian Dornseif on 2012-05-01.
Copyright (c) 2012 Dr. Maximillian Dornseif. Consider it BSD Licensed.
"""

import sys
import subprocess
import os.path
import itertools, collections
import numpy
import math
from pymclevel import mclevel

class Contour(object):        
    def __init__(self):
        # für jede Y "zeile" den minimalen und maximalen X wert speichern. dh maxX[y].
        self.maxX, self.minX =  {}, {}
        # ditto für X 
        self.maxY, self.minY = {}, {}
        
    def trace(self, world_dir):
        """
        Find the contour at the interface between existing and empty
        chunks, then merge appropriately with existing data.
        """
        
        level = mclevel.fromFile(world_dir)

        all_chunks = set(level.allChunks)
        for chunk in all_chunks:
            x, y = chunk
            self.maxX[y], self.minX[y] = max([x, self.maxX.get(y, 0)]), min([x, self.minX.get(y, 0)])
            self.maxY[x], self.minY[x] = max([y, self.maxY.get(x, 0)]), min([y, self.minY.get(x, 0)])

        # jezt ermitteln wir die bounding box
        self.bb_minX, self.bb_maxX = min(self.minX.values()), max(self.maxX.values())
        self.bb_minY, self.bb_maxY = min(self.minY.values()), max(self.maxY.values())
        self.HEIGHT = self.bb_maxX - self.bb_minX
        self.WIDTH = self.bb_maxY - self.bb_minY


def bounding_box(level):
    """Get the bounding Box of all populated chunks."""
    chunks = list(set(level.allChunks))
    maxx, maxy = chunks[0]
    minx, miny = chunks[0]
    for chunk in chunks:
        x, y = chunk
        if level.containsChunk(x, y):
            maxx = max([maxx, x])
            maxy = max([maxy, y])
            minx = min([minx, x])
            miny = min([miny, y])
    return (minx * 16, miny * 16), (maxx * 16, maxy * 16)


def merge(base_world_fn, insert_world_fn):
    print "merging {0} into {1}".format(insert_world_fn, base_world_fn)

    base_level = mclevel.fromFile(base_world_fn)
    bounds = base_level.bounds
    print "World size: \n  {0[0]:7} north to south\n  {0[2]:7} east to west".format(bounds.size)
    print "Smallest and largest points: ({0[0]},{0[2]}), ({1[0]},{1[2]})".format(bounds.origin, bounds.maximum)
    base_n, z, base_w = bounds.origin
    base_s, z, base_e = bounds.maximum
    (base_w, base_s), (base_e, base_n) = bounding_box(base_level)

    insert_level = mclevel.fromFile(insert_world_fn)
    bounds = insert_level.bounds
    print "World size: \n  {0[0]:7} north to south\n  {0[2]:7} east to west".format(bounds.size)
    print "Smallest and largest points: ({0[0]},{0[2]}), ({1[0]},{1[2]})".format(bounds.origin, bounds.maximum)
    print bounding_box(insert_level)

    level_w, z, level_s = bounds.origin
    level_n, z, level_e = bounds.maximum
    (level_w, level_s), (level_e, level_n) = bounding_box(insert_level)


    move_n = (level_n * -1) - 16
    #move_e = level_w * -1
    move_e = base_e + 16

    command ='{0} import {1} {2},0,{3}'.format(base_world_fn, insert_world_fn, move_e, move_n)
    print "python pymclevel/mce.py {0}".format(command)
    subprocess.check_call(['python', 'pymclevel/mce.py'] + command.split())
    open('edit.txt', 'a').write(command + '\n')
    

def main():
    if not len(sys.argv) > 2:
        print "usage:"
        print "    border.py <level_to_change> <level_to_insert> [...]"
        sys.exit(1)

    # we can not handle names with spaces, so fix them
    for insert in sys.argv[2:]:
        merge(sys.argv[1], insert)


if __name__ == '__main__':
	main()

