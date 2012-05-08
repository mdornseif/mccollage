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


    def draw(self, fname):
        """Export drawing of borders"""
        import cairo
        surface = cairo.PSSurface("%s.eps" % fname, self.WIDTH, self.HEIGHT)
        surface.set_eps(True)
        ctx = cairo.Context(surface)
        ctx.set_source_rgb(1, 1, 1)
        ctx.rectangle(0, 0, self.WIDTH, self.HEIGHT)
        ctx.fill()

        ctx.set_source_rgb (0.5, 0.2, 0.3) # Solid color
        # koordinaten nullpunkt in die mitte auf chunk 0, 0 setzen
        ctx.translate(abs(self.bb_minY), abs(self.bb_minX))
        
        # mittelpunkt 
        ctx.arc(0.0, 0.0, 5, 0, math.pi * 2) # Arc(cx, cy, radius, start_angle, stop_angle)
        ctx.stroke()

        ctx.set_source_rgb (0.3, 0.2, 0.5) # Solid color
        ctx.set_line_width(1)
        
        # wir erzeugen jetzt einen einzigen vektorzug, der die outline beschreibt.
        y, x = sorted(self.maxX.items())[0]
        ctx.move_to (x, y)
        for y, x in sorted(self.maxX.items()):
            ctx.line_to (x, y)
        ctx.stroke()

        ctx.set_source_rgb (0.0, 0.0, 0.91) # Solid color
        y, x = sorted(self.maxY.items())[0]
        ctx.move_to (x, y)
        for x, y in sorted(self.maxY.items()):
            ctx.line_to (x, y)
        ctx.stroke()

        ctx.set_source_rgb (0.3, 0.5, 0.3) # Solid color
        y, x = sorted(self.maxX.items())[0]
        ctx.move_to (x, y)
        for y, x in sorted(self.minX.items()):
            ctx.line_to (x, y)
        ctx.stroke()

        ctx.set_source_rgb (0.3, 0.5, 0.8) # Solid color
        y, x = sorted(self.maxY.items())[0]
        ctx.move_to (x, y)
        for x, y in sorted(self.minY.items()):
            ctx.line_to (x, y)
        ctx.stroke()
        print "%s.png" % fname
        surface.write_to_png("%s.png" % fname)
    

def zwei_contouren_zeichnen(a1, a2, xdelta, ydelta):
    "Zeichne zwei kontoruren"
    
    import cairo
    HEIGHT_start = min([y for y, x in a1.items()] + [y+ydelta for y, x in a2.items()])
    HEIGHT_end = max([y for y, x in a1.items()] + [y+ydelta for y, x in a2.items()])
    HEIGHT = HEIGHT_end - HEIGHT_start
    WIDTH_start = min([x for y, x in a1.items()] + [x+xdelta for y, x in a2.items()])
    WIDTH_end = max([x for y, x in a1.items()] + [x+xdelta for y, x in a2.items()])
    WIDTH = WIDTH_end - WIDTH_start
    surface = cairo.PSSurface("combined.eps", WIDTH*3, HEIGHT*3)
    
    surface.set_eps(True)
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(1, 1, 1)
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.fill()

    ctx.translate(WIDTH, HEIGHT_end)
    ctx.set_line_width(1)
    
    ctx.set_source_rgb (0.5, 0.2, 0.3) # Solid color
    y, x = sorted(a1.items())[0]
    ctx.move_to (x, y)
    for y, x in sorted(a1.items()):
        ctx.line_to (WIDTH_end, y)
        ctx.line_to (x, y)
    ctx.stroke()

    # 2. welt
    ctx.set_source_rgb (0.2, 0.2, 0.5) # Solid color
    y, x = sorted(a2.items())[0]
    ctx.move_to (x, y+ydelta)
    for y, x in sorted(a2.items()):
        ctx.line_to(WIDTH_start, y+ydelta)
        ctx.line_to(x+xdelta, y+ydelta)
    ctx.stroke()
    y, x = sorted(a2.items())[0]
    ctx.move_to (x, y)
    for y, x in sorted(a2.items()):
        ctx.line_to(x, y)
    ctx.stroke()

    ctx.set_source_rgb (0.1, 0.1, 0.1) # Solid color
    ctx.move_to (0, HEIGHT_start)
    ctx.line_to (0, HEIGHT_end)
    ctx.stroke()

    ctx.set_source_rgb (0.9, 0.9, 0.9) # Solid color
    ctx.move_to (WIDTH_start, 0)
    ctx.line_to (WIDTH_end, 0)
    ctx.stroke()

    ctx.set_source_rgb (1, 0, 0) # Solid color
    ctx.move_to (min([x for y, x in a1.items()]), HEIGHT_start)
    ctx.line_to (min([x for y, x in a1.items()]), HEIGHT_end)
    ctx.stroke()

    ctx.set_source_rgb (0,0,1) # Solid color
    ctx.move_to (max([x for y, x in a2.items()]), HEIGHT_start)
    ctx.line_to (max([x for y, x in a2.items()]), HEIGHT_end)
    ctx.stroke()

    ctx.set_source_rgb (0,1,0) # Solid color
    ctx.move_to (max([x+xdelta for y, x in a2.items()]), HEIGHT_start)
    ctx.line_to (max([x+xdelta for y, x in a2.items()]), HEIGHT_end)
    ctx.stroke()

    surface.write_to_png("combined.png")
    

def kollision_h(a1, a2, xdelta, ydelta):
    for y, x in sorted(a2.items()):
        newx = x + xdelta
        if newx >= a1.get(y+ydelta, 0):
            return True
    return False


def kollision_v(a1, a2, xdelta, ydelta):
    for y, x in sorted(a2.items()):
        newx = x + xdelta
        if newx >= a1.get(y+ydelta):
            return True
    return False


def merge(base_world_fn, insert_world_fn):
    print "merging {0} into {1}".format(insert_world_fn, base_world_fn)

    base_world = Contour()
    base_world.trace(base_world_fn)
    insert_world = Contour()
    insert_world.trace(insert_world_fn)
    print vars(base_world)
    print "Bounding box base world: [({bb_minX}, {bb_minY}) ; ({bb_maxX}, {bb_maxY})]".format(**vars(base_world))
    print "Bounding box insert world: [({bb_minX}, {bb_minY}) ; ({bb_maxX}, {bb_maxY})]".format(**vars(insert_world))
        
    # the maximum displacement possible and also needed to get a fit
    maxydelta = insert_world.bb_minY - base_world.bb_minY
    minydelta = base_world.bb_maxY
    print "[%s ; %s]" % (minydelta, maxydelta)
        
    def finde_h():
        xdelta = base_world.bb_minX
        xdelta = xdelta - insert_world.WIDTH -1
        ydelta = base_world.bb_minY
        lastworking = (maxydelta, 0)
        lastworking = None
        while True:
            if kollision_h(base_world.minX, insert_world.maxX, xdelta, ydelta):
                ydelta = minydelta
                while True:
                    if kollision_h(base_world.minX, insert_world.maxX, xdelta, ydelta):
                        ydelta += 1
                    else:
                        lastworking = (xdelta, ydelta)
                        break
                    if ydelta >= maxydelta:
                        return lastworking
            else:
                lastworking = (xdelta, ydelta)                 
            xdelta += 1
            if xdelta > 100:
                # this shouldn't happen
                return lastworking
        return lastworking

    xdelta, ydelta = finde_h()
    # das Ergebnis zeichnen
    #zwei_contouren_zeichnen(base_world.minX, insert_world.maxX, xdelta, ydelta)
    
    command ='{0} import {1} {2},0,{3}'.format(base_world_fn, insert_world_fn, (xdelta - insert_world.bb_maxY) * 16, ydelta * 16)
    print "python pymclevel/mce.py {0}".format(command)
    subprocess.check_call(['python', 'pymclevel/mce.py'] + command.split())
    open('edit.txt', 'a').write(command + '\n')
    

def main():
    if len(sys.argv) not in [3, 4]:
        print "usage:"
        print "    border.py <level_to_change> <level_to_insert>"
        print "or"
        print "    border.py <level_to_change> <dir_with_levels_to_insert> <dir_to_store_inserted_levels>"
        sys.exit(1)

    # we can not handle names with spaces, so fix them
    if len(sys.argv) == 3:
        merge(sys.argv[1], sys.argv[2])
    if len(sys.argv) == 4: 
        for lname in os.listdir(sys.argv[2]):
            print lname
            if lname.startswith('.'):
                continue
            lpath = os.path.join(sys.argv[2], lname)
            if ' ' in lpath:
                print "fixing filename {0}".format(lpath)
                os.rename(lpath, lpath.replace(' ', '_'))
                continue  # skip this world for now
            print "{0} in {1}".format(lpath, sys.argv[1])
            merge(sys.argv[1], lpath)
            print "mv {0} {1}".format(lpath, os.path.join(sys.argv[3], lname))
            os.rename(lpath, os.path.join(sys.argv[3], lname))


if __name__ == '__main__':
	main()

