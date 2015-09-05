#Cell Matrix - Copyright (C) 2015
#Released under the GPL3 License

from __future__ import division
import env
pygame = env.engine
interphase = env.interface


class MatrixInterface(interphase.Interface):

    def __init__(self, matrix):
        self.matrix = matrix
        interphase.Interface.__init__(self, position=((self.matrix.width*env.size)//2,(self.matrix.height*env.size)-47), color=(15,30,50), size=(350,96), control_minsize=(41,41), control_size='auto', control_response=100, moveable=True, position_offset=(0,88), font_color=(50,150,200), button_image='button.png', scroll_button='vertical')
        pygame.draw.rect(self.get_panel_image(True), (50,60,100), (162,28,178,48), 1)
        img = pygame.Surface((100,100), pygame.SRCALPHA)
        img.fill((50,50,50,150))
        self.set_control_image(surface=img)
        self.dir = {'N':(0,-1), 'S':(0,1), 'W':(-1,0), 'E':(1,0), 'NW':(-1,-1), 'NE':(1,-1), 'SW':(-1,1), 'SE':(1,1)}
        self.panel_interact = False
        self.width, self.height = self.get_size()
        if env.platform == 'js':
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
            control_outline = True,
            activated_toggle='lock')
        if env.platform == 'js':
            self.add(
                identity = 'Textbox',
                control_type = 'control_toggle',
                position = (20,90),
                size = 'auto_width',
                control_list = ['Input pattern'],
                tip_list = ['Toggle Textbox'],
                activated_toggle = False,
                control_outline = True)
        self.add(
            identity = 'PatternLoad',
            control_type = 'control_toggle',
            position = (235,86),
            size = 'auto_width',
            control_list = ['LOAD'],
            font_size = 8,
            tip_list = ['Retrieve from file'],
            control_outline = True)
        self.add(
            identity = 'PatternGet',
            control_type = 'control_toggle',
            position = (265,86),
            size = 'auto_width',
            control_list = ['GET'],
            font_size = 8,
            tip_list = ['Retrieve from clipboard'],
            control_outline = True)
        self.add(
            identity = 'Patterns',
            control_type = 'control_select',
            position = (250,16),
            size = (64,18),
            control_list = ['Patterns'],
            tip_list = ['Game of Life Patterns'],
            activated_toggle = False,
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
            identity = '__Fix',
            control_type = 'control_toggle',
            position = (324,86),
            color = (0,20,30),
            font_color = (0,120,160),
            font_size = 8,
            control_list = ['!'],
            control_outline = True)
        self.add(
            identity = '__Help',
            control_type = 'control_toggle',
            position = (340,86),
            color = (0,20,30),
            font_color = (0,120,160),
            font_size = 8,
            control_list = ['?'],
            control_outline = True)
        self.get_control('Patterns').set_enabled(False)
        self.get_control('PatternInfo').set_active(False)

    def load_pattern(self):
        ctrl = self.get_control('Patterns')
        current_id = self.matrix.pattern_id
        pattern = []
        try:
            pattern_file = open('pattern.txt')
        except IOError:
            return
        for line in pattern_file:
            if line.startswith('//'):
                continue
            if line.strip():
                pattern.append(line)
            else:
                if pattern:
                    self.matrix.pattern_id += 1
                    self.matrix.patterns[self.matrix.pattern_id] = ''.join(pattern)
                    if self.matrix.pattern_id > 1:
                        ctrl.set_list(['Pattern '+str(self.matrix.pattern_id)], append=True)
                    else:
                        ctrl.set_list(['Pattern '+str(self.matrix.pattern_id)])
                    pattern[:] = []
        pattern_file.close()
        if not ctrl.is_enabled():
            ctrl.set_tip(['Game of Life Patterns'])
            ctrl.set_enabled(True)
            ctrl.reset()
            self.get_control('PatternInfo').set_value(self.matrix.patterns[1])
            self.get_control('PatternInfo').set_active(True)
        elif ctrl.is_activated():
            ctrl.set_activated(False)

    def retrieve_pattern(self):
        pattern = self.get_clipboard()
        if pattern:
            self.matrix.pattern_id += 1
            self.matrix.patterns[self.matrix.pattern_id] = pattern
            ctrl = self.get_control('Patterns')
            if self.matrix.pattern_id > 1:
                ctrl.set_list(['Pattern '+str(self.matrix.pattern_id)], append=True)
                ctrl.reset()
                for i in range(self.matrix.pattern_id-1):
                    ctrl.next()
            else:
                ctrl.set_list(['Pattern '+str(self.matrix.pattern_id)])
            if not ctrl.is_enabled():
                ctrl.set_tip(['Game of Life Patterns'])
                ctrl.set_enabled(True)
                self.get_control('PatternInfo').set_active(True)
            elif ctrl.is_activated():
                ctrl.set_activated(False)
            self.get_control('PatternInfo').set_value(self.matrix.patterns[self.matrix.pattern_id])

    def get_pattern(self):
        ctrl = self.get_control('Patterns')
        if ctrl.is_activated():
            pattern = self.matrix.patterns[int(ctrl.value.split(' ')[-1])]
            return pattern
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
        if self.panel_interact != state.panel_interact:
            self.panel_interact = state.panel_interact
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
                self.get_control('PatternInfo').set_value(self.matrix.patterns[int(state.value.split(' ')[-1])])
            elif state.control == 'PatternLoad':
                self.load_pattern()
            elif state.control == 'PatternGet':
                self.retrieve_pattern()
            elif state.control == 'Textbox':
                pygame.display.textarea.toggle()
            elif state.control == 'Rate':
                self.matrix.set_tick(int(state.value.split(' ')[-1]))
            elif state.control == '__Fix':
                self.set_moveable('Fixed')
            elif state.control == '__Help':
                self.set_tips_display()
            self.matrix.panel_update = True
        if state.panel_update:
            self.matrix.panel_update = True

