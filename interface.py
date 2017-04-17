#Cell Matrix - Copyright (C) 2015
#Released under the GPL3 License

from __future__ import division
import env
pygame = env.engine
interphase = env.interface


class MatrixInterface(interphase.Interface):

    def __init__(self, matrix):
        self.matrix = matrix
        interphase.Interface.__init__(self,
                position=((self.matrix.width*env.size)//2,(self.matrix.height*env.size)-47),
                color=(15,30,50), size=(350,96), control_minsize=(41,41),
                control_size='auto', control_response=100, moveable=False,
                position_offset=(0,88), font_color=(50,150,200),
                button_image='button.png', scroll_button='vertical')
        pygame.draw.rect(self.get_panel_image(True), (50,60,100), (162,28,178,48), 1)
        img = pygame.Surface((100,100), pygame.SRCALPHA)
        img.fill((50,50,50,150))
        self.set_control_image(surface=img)
        self.dir = {'N':(0,-1), 'S':(0,1), 'W':(-1,0), 'E':(1,0), 'NW':(-1,-1), 'NE':(1,-1), 'SW':(-1,1), 'SE':(1,1)}
        self.width, self.height = self.get_size()
        self.set_moveable()
        self.set_moveable('Fixed')
        self.panel_up = True
        if env.platform == 'js':
            self.add_controls_js()
            pygame.display.textbox_init()

    def add_controls(self):
        self.add(
            identity = 'Reset',
            control_type = 'control_toggle',
            position = (26,19),
            size = 'min_width',
            control_list = ['Reset'],
            tip_list = ['Reset matrix'],
            control_outline = True)
        self.add(
            identity = 'Clear',
            control_type = 'control_toggle',
            position = (26,39),
            size = 'min_width',
            control_list = ['Clear'],
            tip_list = ['Clear matrix'],
            control_outline = True)
        self.add(
            identity = 'Edit',
            control_type = 'control_toggle',
            position = (26,59),
            size = 'min_width',
            control_list = ['Edit'],
            tip_list = ['Edit matrix'],
            control_response = 0,
            control_outline = True,
            activated_toggle='lock')
        self.add(
            identity = 'PatternLoad',
            control_type = 'control_toggle',
            position = (235,86),
            size = 'auto_width',
            control_list = ['LOAD'],
            font_size = 8,
            tip_list = ['Retrieve from file'],
            control_response = 0,
            control_outline = True)
        self.add(
            identity = 'PatternGet',
            control_type = 'control_toggle',
            position = (265,86),
            size = 'auto_width',
            control_list = ['GET'],
            font_size = 8,
            tip_list = ['Retrieve from clipboard'],
            control_response = 0,
            control_outline = True)
        self.add(
            identity = 'Patterns',
            control_type = 'control_select',
            position = (250,18),
            size = (64,18),
            control_list = ['Patterns'],
            tip_list = ['Game of Life Patterns'],
            activated_toggle = False,
            control_response = 200,
            control_outline = True,
            split_text = False)
        self.add(
            identity = 'PatternInfo',
            control_type = 'textbox',
            position = (251,52),
            size = (176,46),
            color = (50,50,50),
            font_color = (255,255,255),
            font_type = 'courier',
            font_size = 8,
            control_list = [],
            tip_list = ['Pattern Information'],
            activated_toggle = False,
            control_outline = True)
        self.add(
            identity = 'Rate',
            control_type = 'control_select',
            position = (26,79),
            size = 'min_width',
            control_list = ['Rate 1','Rate 2','Rate 3','Rate 4'],
            tip_list = ['Processing rate'],
            split_text = False,
            control_response = 200,
            control_outline = True,
            reverse = True)
        for ident, tip, img, pos in ( ('N',['North'],['control_n.png'],(111,25)), ('S',['South'],['control_s.png'],(111,75)), ('W',['West'],['control_w.png'],(86,50)), ('E',['East'],['control_e.png'],(136,50)) ):
            self.add(
                identity = ident,
                control_type = 'control_toggle',
                position = pos,
                size = (25,25),
                control_list = [''],
                tip_list = tip,
                control_image = img,
                control_response = 25)
        for ident, tip, pos in ( ('NW',['North-West'],(86,25)), ('NE',['North-East'],(136,25)), ('SW',['South-West'],(86,75)), ('SE',['South-East'],(136,75)), ('X',['Center'],(111,50)) ):
            self.add(
                identity = ident,
                control_type = 'control_toggle',
                position = pos,
                size = (25,25),
                control_list = [''],
                tip_list = tip,
                control_response = 25)
        self.add(
            identity = '__TopFix',
            control_type = 'control_toggle',
            position = (self.get_size()[0]//2,4),
            size = (340,8),
            control_list = [''],
            control_image = 'none',
            control_response = 0,
            control_outline = False)
        self.add(
            identity = '__Fix',
            control_type = 'control_toggle',
            position = (324,86),
            color = (0,20,30),
            font_color = (0,120,160),
            font_size = 8,
            control_list = ['!'],
            control_response = 0,
            control_outline = True)
        self.add(
            identity = '__Help',
            control_type = 'control_toggle',
            position = (340,86),
            color = (0,20,30),
            font_color = (0,120,160),
            font_size = 8,
            control_list = ['?'],
            control_response = 0,
            control_outline = True)
        self.ctrl_patterns = self.get_control('Patterns')
        self.ctrl_patterninfo = self.get_control('PatternInfo')
        self.ctrl_patterninfo.set_active(False)
        self.ctrl_topfix = self.get_control('__TopFix')
        self.ctrl_topfix.set_enabled(False)

    def add_controls_js(self):
        self.add(
            identity = 'Textbox',
            control_type = 'control_toggle',
            position = (280,86),
            size = 'auto_width',
            control_list = ['v','^'],
            font_size = 8,
            tip_list = ['Toggle Textbox'],
            control_response = 0,
            control_outline = True)

    def load_pattern(self):
        if not env.platform == 'js':
            try:
                pattern_file = open('pattern.txt')
                patterns = pattern_file.read()
                pattern_file.close()
            except IOError:
                try:
                    from pattern import patterns
                except ImportError:
                    return
        else:
            try:
                from pattern import patterns
            except ImportError:
                return
        if patterns:
            self.register_pattern(patterns)

    def retrieve_pattern(self):
        pattern = self.get_clipboard()
        if pattern:
            self.register_pattern(pattern)

    def register_pattern(self, patterns):
        current_id = self.matrix.pattern_id
        pattern = []
        for line in patterns.split('\n'):
            if line.startswith('//'):
                continue
            if line.strip():
                pattern.append(line)
            else:
                if pattern:
                    self.set_pattern('\n'.join(pattern))
                    pattern[:] = []
        else:
            if pattern:
                self.set_pattern('\n'.join(pattern))
        if self.matrix.pattern_id == current_id:
            return
        if not self.ctrl_patterninfo.is_active():
            self.ctrl_patterninfo.set_active(True)
        if self.ctrl_patterns.is_activated():
            self.ctrl_patterns.set_activated(False)
        self.ctrl_patterns.set_tip(['Game of Life Patterns'])
        if current_id:
            self.ctrl_patterns.set_list_index(current_id)
        else:
            self.ctrl_patterns.reset()
        self.ctrl_patterninfo.set_value(self.matrix.patterns[int(self.ctrl_patterns.get_value().split(' ')[-1])])

    def set_pattern(self, pattern):
        self.matrix.pattern_id += 1
        self.matrix.patterns[self.matrix.pattern_id] = pattern
        if self.matrix.pattern_id > 1:
            self.ctrl_patterns.set_list(['Pattern '+str(self.matrix.pattern_id)], append=True)
        else:
            self.ctrl_patterns.set_list(['Pattern '+str(self.matrix.pattern_id)])

    def get_pattern(self):
        if self.matrix.patterns and self.ctrl_patterns.is_activated():
            return self.matrix.patterns[int(self.ctrl_patterns.value.split(' ')[-1])]
        else:
            return None

    def edit_enable(self, setting=True):
        ctrl = self.get_control('Edit')
        if setting:
            if not ctrl.is_activated():
                ctrl.set_activated(True)
        else:
            if ctrl.is_activated():
                ctrl.set_activated(False)

    def update(self):
        state = interphase.Interface.update(self)
        if state.control:
            if state.control in ('N', 'S', 'W', 'E', 'NW', 'NE', 'SW', 'SE'):
                self.matrix.view_scroll(self.dir[state.control])
            elif state.control == 'X':
                self.matrix.view_reset()
            elif state.control == 'Reset':
                self.matrix.reset_matrix()
            elif state.control == 'Clear':
                self.matrix.clear_matrix()
            elif state.control == 'Edit':
                if state.controls[state.control].is_activated():
                    self.matrix.edit_matrix()
                else:
                    self.matrix.activate()
            elif state.control == 'Patterns':
                if self.matrix.patterns:
                    self.ctrl_patterninfo.set_value(self.matrix.patterns[int(state.value.split(' ')[-1])])
                else:
                    self.ctrl_patterns.set_activated(False)
            elif state.control == 'PatternLoad':
                self.load_pattern()
            elif state.control == 'PatternGet':
                self.retrieve_pattern()
            elif state.control == 'Textbox':
                pygame.display.textarea.toggle()
            elif state.control == 'Rate':
                self.matrix.set_tick(int(state.value.split(' ')[-1]))
            elif state.control in ('__Fix', '__TopFix'):
                self.set_moveable('Fixed')
                self.panel_up = not self.panel_up
                if self.panel_up:
                    self.ctrl_topfix.set_enabled(False)
                else:
                    self.ctrl_topfix.set_enabled(True)
            elif state.control == '__Help':
                self.set_tips_display()
            self.matrix.panel_update = True
        if state.panel_update:
            self.matrix.panel_update = True

