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
        for i in range(100):    #interface issue resolved in v0.87_dev
            self.panel._clock.tick(self.fps)
            if self.fps-1 < self.panel._clock.get_fps() < self.fps+1:
                break
        self.clock = pygame.time.Clock()
        self.dir = {pygame.K_UP:(0,-1), pygame.K_DOWN:(0,1), pygame.K_LEFT:(-1,0), pygame.K_RIGHT:(1,0)}
        self.dir_kp = {pygame.K_KP8:(0,-1), pygame.K_KP2:(0,1), pygame.K_KP4:(-1,0), pygame.K_KP6:(1,0)}
        self.quit = False

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
                    pygame.quit()
                    self.quit = True
                    return self.quit
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.panel.panel_interact:
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
                pygame.quit()
                self.quit = True
        self.clock.tick(self.fps)
        return self.quit


class Interface:
    _clipboard = None
    _clipboard_type = None
    #clipboard code derived from Interphase module

    def __init__(self, matrix):
        self.matrix = None
        self.panel_interact = False

    def get_pattern(self):
        return None

    def edit_enable(self, setting=True):
        return None

    def get_clipboard(self):
        """Retrieve text from clipboard."""
        raise AttributeError, "clipboard unavailable"

    def set_clipboard(self, text):
        """Save text to clipboard."""
        raise AttributeError, "clipboard unavailable"

    def _clipboard_init(self):
        if not Interface._clipboard:
            try:
                from gtk import Clipboard
                Interface._clipboard = Clipboard()
                Interface._clipboard_type = 'gtk'
            except ImportError:
                try:
                    from Tkinter import Tk
                    Interface._clipboard = Tk()
                    Interface._clipboard.withdraw()
                    Interface._clipboard_type = 'tk'
                except ImportError:
                    try:
                        global StringSelection, DataFlavor, UnsupportedFlavorException, IOException, IllegalStateException
                        from java.awt.datatransfer import StringSelection, DataFlavor
                        from java.awt.datatransfer import UnsupportedFlavorException
                        from java.io import IOException
                        from java.lang import IllegalStateException
                        from java.awt import Toolkit
                        Interface._clipboard = Toolkit.getDefaultToolkit().getSystemClipboard()
                        Interface._clipboard_type = 'jtk'
                    except ImportError:
                        try:
                            engine.display.textbox_init()
                            Interface._clipboard = engine.display.textarea
                            Interface._clipboard_type = 'js'
                        except AttributeError:
                            Interface._clipboard = None
                            Interface._clipboard_type = None
        if Interface._clipboard_type == 'gtk':
            self.get_clipboard = self._get_clipboard_gtk
            self.set_clipboard = self._set_clipboard_gtk
        elif Interface._clipboard_type == 'tk':
            self.get_clipboard = self._get_clipboard_tk
            self.set_clipboard = self._set_clipboard_tk
        elif Interface._clipboard_type == 'jtk':
            self.get_clipboard = self._get_clipboard_jtk
            self.set_clipboard = self._set_clipboard_jtk
        elif Interface._clipboard_type == 'js':
            self.get_clipboard = self._get_clipboard_js
            self.set_clipboard = self._set_clipboard_js

    def _get_clipboard_gtk(self):
        text = Interface._clipboard.wait_for_text()
        return text

    def _set_clipboard_gtk(self, text):
        Interface._clipboard.set_text(text)
        Interface._clipboard.store()
        return

    def _get_clipboard_tk(self):
        text = Interface._clipboard.clipboard_get()
        return text

    def _set_clipboard_tk(self, text):
        Interface._clipboard.clipboard_clear()
        Interface._clipboard.clipboard_append(text)

    def _get_clipboard_jtk(self):
        contents = Interface._clipboard.getContents(None)
        if contents != None:
            try:
                text = contents.getTransferData(DataFlavor.stringFlavor)
            except (UnsupportedFlavorException, IOException):
                text = None
        else:
            text = None
        return text

    def _set_clipboard_jtk(self, text):
        try:
            Interface._clipboard.setContents(StringSelection(text), None)
        except IllegalStateException:
            pass
        return

    def _get_clipboard_js(self):
        text = Interface._clipboard.getText()
        return text

    def _set_clipboard_js(self, text):
        Interface._clipboard.setText(text)
        return

    def get_clipboard(self):
        return None

    def is_update(self):
        return False

    def update(self):
        pass

