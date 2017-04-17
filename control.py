#Cell Matrix - Copyright (C) 2015
#Released under the GPL3 License

from __future__ import division
import env
pygame = env.engine


class Control:

    def __init__(self, matrix, panel):
        self.matrix = matrix
        self.panel = panel
        self.fps = 30
        self.clock = pygame.time.Clock()
        self.dir = {pygame.K_UP:(0,-1), pygame.K_DOWN:(0,1), pygame.K_LEFT:(-1,0), pygame.K_RIGHT:(1,0)}
        self.dir_kp = {pygame.K_KP8:(0,-1), pygame.K_KP2:(0,1), pygame.K_KP4:(-1,0), pygame.K_KP6:(1,0)}

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if self.matrix.edit:
                        self.matrix.activate()
                        self.panel.edit_enable(False)
                    self.matrix.reset_matrix()
                elif event.key == pygame.K_c:
                    self.matrix.clear_matrix()
                elif event.key in (pygame.K_e, pygame.K_ESCAPE):
                    if not self.matrix.edit:
                        self.matrix.edit_matrix()
                        self.panel.edit_enable(True)
                    else:
                        self.matrix.activate()
                        self.panel.edit_enable(False)
                elif event.key == pygame.K_p:
                    self.matrix.panel_display = not self.matrix.panel_display
                    self.matrix.clear_panel()
                elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    self.matrix.view_scroll(self.dir[event.key])
                elif event.key in (pygame.K_KP8, pygame.K_KP2, pygame.K_KP4, pygame.K_KP6):
                    self.matrix.view_scroll(self.dir_kp[event.key])
                elif event.key == pygame.K_q:
                    self.matrix.quit = True
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.panel.rect.collidepoint(event.pos):
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
            elif event.type == pygame.QUIT:
                self.matrix.quit = True
        self.clock.tick(self.fps)
        return None

