#Cell Matrix - Copyright (C) 2015
#Released under the GPL3 License

from __future__ import division
import env
pg = env.engine


class Control:

    def __init__(self, matrix, panel):
        self.matrix = matrix
        self.panel = panel
        self.dir = {pg.K_UP:(0,-1), pg.K_DOWN:(0,1), pg.K_LEFT:(-1,0), pg.K_RIGHT:(1,0)}
        self.dir_kp = {pg.K_KP8:(0,-1), pg.K_KP2:(0,1), pg.K_KP4:(-1,0), pg.K_KP6:(1,0)}

    def update(self):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    if self.matrix.edit:
                        self.matrix.activate()
                        self.panel.edit_enable(False)
                    self.matrix.reset_matrix()
                elif event.key == pg.K_c:
                    self.matrix.clear_matrix()
                elif event.key in (pg.K_e, pg.K_ESCAPE):
                    if not self.matrix.edit:
                        self.matrix.edit_matrix()
                        self.panel.edit_enable(True)
                    else:
                        self.matrix.activate()
                        self.panel.edit_enable(False)
                elif event.key == pg.K_p:
                    self.matrix.panel_display = not self.matrix.panel_display
                    self.matrix.clear_panel()
                elif event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT):
                    self.matrix.view_scroll(self.dir[event.key])
                elif event.key in (pg.K_KP8, pg.K_KP2, pg.K_KP4, pg.K_KP6):
                    self.matrix.view_scroll(self.dir_kp[event.key])
                elif event.key == pg.K_q:
                    self.matrix.quit = True
            elif event.type == pg.MOUSEBUTTONDOWN and not self.panel.rect.collidepoint(event.pos):
                if event.button == 1:
                    x = (event.pos[0]//env.size) + self.matrix.view[0]
                    y = (event.pos[1]//env.size) + self.matrix.view[1]
                    pattern = self.panel.get_pattern()
                    if pattern:
                        self.matrix.paste_pattern(x,y,pattern)
                    else:
                        self.matrix.cell_toggle(x,y)
                        self.matrix.change = True
                elif event.button == 3:
                    x = (event.pos[0]//env.size) + self.matrix.view[0]
                    y = (event.pos[1]//env.size) + self.matrix.view[1]
                    self.matrix.paste_pattern(x,y)
                    if self.matrix.edit:
                        self.matrix.change = True
            elif event.type == pg.QUIT:
                self.matrix.quit = True
        return None

