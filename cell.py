#!/usr/bin/env python

"""
Cell Matrix - Implementation of Conway's Game of Life Algorithm
Copyright (C) 2015 James Garnon

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Cell Matrix version 1.0
Download Site: http://gatc.ca
"""

from __future__ import division
import os, sys, math, random
if os.name in ('posix', 'nt', 'os2', 'ce', 'riscos'):
    import pygame
    platform = 'pc'
elif os.name == 'java':
    import pyj2d
    sys.modules['pygame'] = pyj2d
    pygame = pyj2d
    platform = 'jvm'
    if sys.version_info[0:2] == (2,2):
        from sets import Set
else:
    import pyjsdl as pygame
    platform = 'js'

import interphase
interphase.init(pygame)

import env
env.engine = pygame
env.interface = interphase
env.platform = platform
env.size = 8
env.color0 = pygame.Color(0,0,0)
env.color1 = pygame.Color(0,255,0)

from control import Control
from interface import MatrixInterface


class Matrix:

    def __init__(self, width, height):
        self.width, self.height = width, height
        self.size = env.size
        self.color0 = env.color0
        self.color1 = env.color1
        self.rect = pygame.Rect(0, 0, self.size-2, self.size-2)
        self.cell0 = pygame.Surface((self.size-2, self.size-2))
        self.cell0.fill(self.color0)
        self.cell1 = pygame.Surface((self.size-2, self.size-2))
        self.cell1.fill(self.color1)
        self.setPool = []
        self.listPool = []
        self.patterns = {}
        self.pattern_id = 0
        self.screen, self.background, self.control, self.panel, self.clock = self.setup(width,height)
        if self.panel.matrix:
            psize = self.panel.get_size()
            ppos = self.panel.get_position()
            self.panel_clear1 = pygame.Surface(psize)
            self.panel_pos1 = pygame.Rect((ppos[0]-(psize[0]//2),ppos[1]-(psize[1]//2)), psize)
            self.panel_clear1.blit(self.screen, (0,0), self.panel_pos1)     #pyjsdl blit - IndexSizeError - clip area
            self.panel_clear2 = pygame.Surface((psize[0],12))
            self.panel_pos2 = pygame.Rect((ppos[0]-(psize[0]//2),ppos[1]-(psize[1]//2)+88), (psize[0],12))
            self.panel_clear2.blit(self.screen, (0,0), self.panel_pos2)
            self.panel_pos = ppos[1]
            self.panel_display = True
        else:
            self.panel_display = False
        self.display_update = False
        if env.platform in ('pc','jvm'):
            self.xrange = list(range((width//10), width-(width//10)))
            self.yrange = list(range((height//10), height-(height//10)))
        else:
            self.xrange = list(range((width//5), width-(width//5)))
            self.yrange = list(range((height//5), height-(height//5)))
        self.view = [0,0]
        self.scroll = False
        self.grid = {}
        self.grid_cache = {}
        self.cell_seed()
        self.nb = []
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if i == 0 and j == 0:
                    continue
                self.nb.append((i,j))
        self.quit = False
        self.pause = False
        self.edit = False
        self.change = False
        try:
            self.neighbor_set = set()
        except NameError:
            self.neighbor_set = Set()
            self.get_set = self.get_set_alt
        self.neighbors = {}
        self.neighbor_cache_init()
        self.ticks = 6
        self.tick = 0
        self.update_list = []

    def setup(self, w, h):
        screen = pygame.display.get_surface()
        background = pygame.Surface((w*self.size,h*self.size))
        background.fill((20,40,60))
        for x in range(w):
            for y in range(h):
                background.blit(self.cell0, ((x*self.size)+1, (y*self.size)+1))
        screen.blit(background, (0,0))
        pygame.display.flip()
        pygame.display.set_caption('Cell Matrix')
        icon = pygame.image.load(os.path.join('data', 'icon.png'))
        pygame.display.set_icon(icon)
        pygame.event.set_blocked(pygame.MOUSEMOTION)
        pygame.key.set_repeat(100,10)
        panel = MatrixInterface(self)
        panel._clipboard_init()
        control = Control(self, panel)
        clock = pygame.time.Clock()
        return screen, background, control, panel, clock

    def set_tick(self, value):
        ticks = {1:6, 2:3, 3:1, 4:0}[value]
        if self.ticks != ticks:
            self.ticks = ticks
            self.tick = self.ticks

    def get_set(self):
        if self.setPool:
            s = self.setPool.pop()
            s.clear()
            return s
        else:
            return set()

    def get_set_alt(self):
        if self.setPool:
            s = self.setPool.pop()
            s.clear()
            return s
        else:
            return Set()

    def get_list(self):
        if self.listPool:
            lst = self.listPool.pop()
            lst[:] = []
            return lst
        else:
            return []

    def edit_matrix(self):
        self.pause = True
        self.edit = True
        self.change = True

    def activate(self):
        self.edit = False
        self.pause = False

    def view_scroll(self, direction, view_change=1):
        self.view[0] += (direction[0]*view_change)
        self.view[1] += (direction[1]*view_change)
        self.change = True
        self.scroll = True

    def view_reset(self):
        self.view[0] = 0
        self.view[1] = 0
        self.change = True
        self.scroll = True

    def neighbor_cache_init(self):
        if env.platform in ('pc','jvm'):
            for x in range(-self.width//2, self.width+(self.width//2)):
                for y in range(-self.height//2, self.height+(self.height//2)):
                    self.neighbor_cache(x,y)
        else:
            for x in range(0, self.width):
                for y in range(0, self.height):
                    self.neighbor_cache(x,y)

    def cell_seed(self):
        for x in self.xrange:
            for y in self.yrange:
                if random.random() > 0.9:
                    self.grid[(x,y)] = None

    def reset_matrix(self):
        self.clear_matrix()
        self.cell_seed()
        self.tick = 0
        if self.edit:
            self.panel.edit_enable(False)
            self.activate()

    def clear_matrix(self):
        self.grid.clear()
        self.view[0] = 0
        self.view[1] = 0
        self.screen.blit(self.background, (0,0))
        pygame.display.flip()

    def clear_panel(self):
        self.panel_pos = self.panel.get_position()[1]
        if self.panel_pos != 441:
            self.screen.blit(self.panel_clear1, self.panel_pos1)
            self.update_list.append(self.panel_pos1)
        else:
            self.screen.blit(self.panel_clear2, self.panel_pos2)
            self.update_list.append(self.panel_pos2)

    def paste_pattern(self, x, y, pattern=None):
        if pattern is None:
            pattern = self.panel.get_clipboard()
            if not pattern:
                return
        pattern_start = False
        for line in pattern.split('\n'):
            if not line or self.check_pattern_comment(line):
                if not pattern_start:
                    continue
                else:
                    break
            else:
                pattern_start = True
            for i, char in enumerate(line):
                if char == '.':
                    pass
                elif char in ('O','*'):
                    self.grid[x+i,y] = None
            y += 1

    def check_pattern_comment(self, line):
        try:
            return line.startswith(('!','#','//'))
        except TypeError:
            for ch in ('!','#','//'):
                if line.startswith(ch):
                    return True
            else:
                return False

    def cell_add(self, x, y):
        self.grid[(x, y)] = None
        self.update_list.append(pygame.Rect(x*self.size, y*self.size, self.size, self.size))

    def cell_remove(self, x, y):
        if self.grid[(x,y)]:
            self.setPool.append(self.grid_cache[(x,y)])
        del self.grid[(x,y)]
        self.singlecell_clear((x,y))

    def cell_toggle(self, x, y):
        if (x,y) not in self.grid:
            self.cell_add(x,y)
        else:
            self.cell_remove(x,y)

    def neighbor_cache(self, x, y):
        self.neighbors[(x,y)] = self.neighbor_generate(x,y)

    def neighbor_generate(self, x, y):
        neighbors = self.get_list()
        for i,j in self.nb:
            neighbors.append((x+i,y+j))
        return neighbors

    def neighbor_locate(self, x, y):
        if (x,y) in self.neighbors:
            neighbor = self.get_set()
            for cell in self.neighbors[(x,y)]:
                if cell not in self.grid:
                    neighbor.add(cell)
            return neighbor
        else:
            neighbors = self.neighbor_generate(x,y)
            neighbor = self.get_set()
            for cell in neighbors:
                if cell not in self.grid:
                    neighbor.add(cell)
            return neighbor

    def neighbor_count(self, x, y):
        if (x,y) in self.neighbors:
            count = 0
            for cell in self.neighbors[(x,y)]:
                if cell in self.grid:
                    count += 1
            return count
        else:
            neighbors = self.neighbor_generate(x,y)
            count = 0
            for cell in neighbors:
                if cell in self.grid:
                    count += 1
            return count

    def grid_clear(self):
        for cell in self.grid_cache:
            self.setPool.append(self.grid_cache[cell])
        self.grid_cache.clear()

    def cell_live(self):
        for cell in self.grid:
            self.grid[cell] = self.neighbor_locate(cell[0],cell[1])
            if 1 < (8-len(self.grid[cell])) < 4:
                self.grid_cache[cell] = None
            self.neighbor_set.update(self.grid[cell])

    def cell_reprod(self):
        for cell in self.neighbor_set:
            if self.neighbor_count(cell[0],cell[1]) == 3:
                self.grid_cache[cell] = None
        self.neighbor_set.clear()

    def cell_growth(self):
        self.grid_clear()
        self.cell_live()
        self.cell_reprod()
        grid = self.grid
        self.grid = self.grid_cache
        self.grid_cache = grid

    def singlecell_clear(self, cell):
        x = self.view[0]
        y = self.view[1]
        if (x <= cell[0] < self.width+x) and (y <= cell[1] < self.height+y):
            self.rect.x = ((cell[0]-x)*self.size)+1
            self.rect.y = ((cell[1]-y)*self.size)+1
            self.update_list.append( self.screen.blit(self.cell0, self.rect) )

    def cell_clear_select(self, height):
        x = self.view[0]
        y = self.view[1]
        for cell in self.grid_cache:
            if (x <= cell[0] < self.width+x) and (y <= cell[1] < self.height+y):
                self.rect.x = ((cell[0]-x)*self.size)+1
                self.rect.y = ((cell[1]-y)*self.size)+1
                self.update_list.append( self.screen.blit(self.cell0, self.rect) )

    def cell_draw_select(self, height):
        x = self.view[0]
        y = self.view[1]
        for cell in self.grid:
            if (x <= cell[0] < self.width+x) and (y <= cell[1] < self.height+y):
                self.rect.x = ((cell[0]-x)*self.size)+1
                self.rect.y = ((cell[1]-y)*self.size)+1
                self.update_list.append( self.screen.blit(self.cell1, self.rect) )

    def cell_display_select(self):
        if not self.scroll:
            self.cell_clear_select(self.panel_pos)
            self.cell_draw_select(self.panel_pos)

    def cell_clear(self):
        x = self.view[0]
        y = self.view[1]
        for cell in self.grid_cache:
            if (x <= cell[0] < self.width+x) and (y <= cell[1] < self.height+y):
                self.rect.x = ((cell[0]-x)*self.size)+1
                self.rect.y = ((cell[1]-y)*self.size)+1
                self.update_list.append( self.screen.blit(self.cell0, self.rect) )

    def cell_draw(self):
        x = self.view[0]
        y = self.view[1]
        for cell in self.grid:
            if (x <= cell[0] < self.width+x) and (y <= cell[1] < self.height+y):
                self.rect.x = ((cell[0]-x)*self.size)+1
                self.rect.y = ((cell[1]-y)*self.size)+1
                self.update_list.append( self.screen.blit(self.cell1, self.rect) )

    def cell_display(self):
        if not self.scroll:
            self.cell_clear()
            self.cell_draw()
        else:
            self.screen.blit(self.background, (0,0))
            self.cell_draw()

    def update(self):
        self.update_list[:] = []
        if self.panel_display:
            self.clear_panel()
        self.panel.update()
        self.control.update()
        if not self.pause:
            if not self.tick:
                self.cell_growth()
                self.cell_display()
                self.tick = self.ticks
            else:
                self.tick -= 1
                if self.change:
                    self.cell_display()
                    self.change = False
                else:
                    if self.panel_display:
                        self.cell_display_select()
        else:
            if self.change:
                self.cell_display()
                self.change = False
            else:
                if self.panel_display:
                    self.cell_display_select()
        if self.panel_display:
            self.panel.draw(self.screen)
        if not self.scroll:
            pygame.display.update(self.update_list)
        else:
            pygame.display.update()
            self.scroll = False
        self.clock.tick(30)


def setup(w,h):
    pygame.init()
    pygame.display.set_mode((w*env.size,h*env.size))


def main():
    w, h = 60, 50
    setup(w,h)
    matrix = Matrix(w,h)
    while not matrix.quit:
        matrix.update()


matrix = None
def run():
    global matrix
    matrix.update()

def pre_run():
    global matrix
    matrix = Matrix(60, 50)
    pygame.display.setup(run)

def main_js():
    setup(60, 50)
    img = ['data/control_n.png', 'data/control_s.png', 'data/control_w.png',
            'data/control_e.png', 'data/button.png', 'data/icon.png']
    pygame.display.setup(pre_run, img)


if __name__ == '__main__':
    if platform != 'js':
        main()
    else:
        main_js()

