''' Library providing program pages class for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

from data_types import ChainMapTuple, GenOptions
import midi_tools as mt
import ui
from ui_pages import Page
from ui_blocks import TitleBar, SelectBlock

_NONE                   = const(-1)
_NOTE_OFF_OFF           = const(-1) 

_MAX_ROUTING_LAYERS     = const(4)
_NR_OUT_PORTS           = const(6)

_ADD_NEW_LABEL          = '[add new]'
_EMPTY_OPTIONS_LONG     = ('____',)
_EMPTY_OPTIONS_SHORT    = ('___',)

_NOTE_OPTIONS           = GenOptions(128, first_options=('___',), func=mt.number_to_note)
_NOTE_OFF_OPTIONS       = GenOptions(922, 80, ('____', 'off', 'pulse', 'toggle'), str, ' ms')
_PROGRAM_CHANGE_OPTIONS = GenOptions(128, 1, ('___',), str)
_BANK_SELECT_OPTIONS    = GenOptions(128, 0, ('___',), str)

_NEW_PROGRAM            = 'NEW PROGRAM'

_MAX_LABEL_LENGTH       = const(33)

_SUB_PAGES              = const(5)
_SUB_PAGE_MAPPING       = const(0)
_SUB_PAGE_NOTE          = const(1)
_SUB_PAGE_NOTE_OFF      = const(2)
_SUB_PAGE_PROGRAM       = const(3)
_SUB_PAGE_BANK          = const(4)

_SELECT_SUB_PAGE        = const(-1)
_NAME                   = const(0)
_INPUT_DEVICE           = const(1)
_INPUT_PRESET           = const(2)
_FIRST_OUTPUT_DEVICE    = const(3)
_FIRST_OUTPUT_PRESET    = const(4)
_FIRST_NOTE             = const(3)
_FIRST_NOTE_OFF         = const(3)
_FIRST_PROGRAM          = const(0)
_FIRST_BANK_MSB         = const(0)
_FIRST_BANK_LSB         = const(1)

_MAPPING_DEVICE_COL     = const(0)
_MAPPING_PRESET_COL     = const(1)
_MAPPING_NOTE_COL       = const(2)
_MAPPING_NOTE_OFF_COL   = const(3)

_POP_UP_TEXT_EDIT       = const(0)
_POP_UP_SELECT          = const(1)
_POP_UP_MENU            = const(2)
_POP_UP_CONFIRM         = const(3)

_MENU_ITEMS_WO_SAVE     = ('rename', 'move backward', 'move forward', 'move to...')
_MENU_ITEMS_W_SAVE      = ('save', 'rename', 'move backward', 'move forward', 'move to...')

_RENAME_WO              = const(0)
_MOVE_BACKWARD_WO       = const(1)
_MOVE_FORWARD_WO        = const(2)
# _MOVE_TO_WO             = const(3)

_SAVE_W                 = const(0)
_RENAME_W               = const(1)
_MOVE_BACKWARD_W        = const(2)
_MOVE_FORWARD_W         = const(3)
# _MOVE_TO_W              = const(4)

_CONFIRM_DELETE         = const(128) # needs to be higher than block ids
_CONFIRM_SAVE           = const(129)
_CONFIRM_REPLACE        = const(130)

_SELECT_POSITION        = const(0)

_CC_BANK_MSB            = const(0x00)
_CC_BANK_LSB            = const(0x20)

class PageProgram(Page):
    '''monitor page class; initiated once by ui.__init__'''

    def __init__(self, id: int, x: int, y: int, w: int, h: int, visible: bool) -> None:
        super().__init__(id, x, y, w, h, visible)
        ###### only for testing or screenshot
        # self.sub_page = 0
        self.program_name = ''
        self.output_devices_tuple = ()
        self.mapping_settings = []
        self.program_settings = [['', _NONE] for _ in range(_NR_OUT_PORTS)]
        self.bank_settings = [['', [_NONE, _NONE]] for _ in range(_NR_OUT_PORTS)]
        self.page_is_built = False
        self._build_page()

    def program_change(self) -> None:
        '''update page after program change (also needed to trigger draw); called by ui.program_change'''
        _ui = ui
        _router = _ui.router
        if _router.is_new_program:
            self.program_name = _ADD_NEW_LABEL
        else:
            self.program_name = _ui.data.routing_programs[_router.active_program_number][0]
        self.bank_msb = 0
        if self.visible:
            self._load()
        else:
            selected_block = self.selected_block
            blocks = self.blocks
            if selected_block != 0:
                blocks[selected_block].update(redraw=False)
                blocks[0].update(True, redraw=False)
            self.selected_block = 0

    def encoder(self, encoder_nr: int, value: int, page_button: bool) -> None:
        '''process encoder input at page level (ui.process_encoder > Page.encoder/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by ui.process_encoder_input'''
        self.bank_msb = 0
        super().encoder(encoder_nr, value, page_button)

    def process_user_input(self, id: int, value: int = _NONE, text: str = '',
                           button_encoder_0: bool = False, button_encoder_1: bool = False) -> None:
        '''process user input at page level (ui.ui.set_user_input_dict > global user_input_dict > ui.process_user_input >
        Page/PagesTab.process_user_input); called by ui.process_user_input'''
        sub_page = self.sub_page
        if id == _SELECT_SUB_PAGE:
            if button_encoder_0 or button_encoder_1 or value == _NONE or value == sub_page:
                return
            self.bank_msb = 0
            self._set_sub_page(value)
            self._load()
            return
        if sub_page == _SUB_PAGE_MAPPING or sub_page == _SUB_PAGE_NOTE or sub_page == _SUB_PAGE_NOTE_OFF:
            if button_encoder_0 and id == _NAME:
                ui.ui.pop_ups[_POP_UP_CONFIRM].open(self, _CONFIRM_DELETE, 'delete?', self._callback_confirm)
            elif button_encoder_1 and id == _NAME:
                _router = ui.router
                items = _MENU_ITEMS_W_SAVE if _router.program_changed else _MENU_ITEMS_WO_SAVE
                ui.ui.pop_ups[_POP_UP_MENU].open(self, _NAME, items, callback_func=self._callback_menu)
            else:
                _router = ui.router
                if id == _NAME:
                    if _router.active_program_number == value:
                        return
                    if _router.program_changed:
                        self.next_program = value
                        ui.ui.pop_ups[_POP_UP_CONFIRM].open(self, _CONFIRM_SAVE, 'save changes?', self._callback_confirm)
                    else:
                        _router.update(False, False, False, False, False, False, value)
                elif id == _INPUT_DEVICE:
                    if value == _NONE or value == _router.input_device_value:
                        return
                    if _router.is_new_program:
                        _router.add_program(_NEW_PROGRAM)
                    ui.ui.set_trigger(value)
                elif id == _INPUT_PRESET:
                    if value == _NONE or value == _router.input_preset_value:
                        return
                    ui.ui.set_trigger(preset=value)
                elif sub_page == _SUB_PAGE_MAPPING:
                    if _router.is_new_program:
                        _router.add_program(_NEW_PROGRAM)
                    row = (id - _FIRST_OUTPUT_DEVICE) // 2
                    col = (id - _FIRST_OUTPUT_DEVICE) % 2
                    settings = self.mapping_settings
                    additional_rows = row - len(settings) + 1
                    if additional_rows > 0:
                        for _ in range(additional_rows):
                            settings.append(['', '', _NONE, _NOTE_OFF_OFF])
                    if value == 0:
                        text = ''
                    settings[row][col] = text
                    if col == _MAPPING_DEVICE_COL:
                        settings[row][_MAPPING_PRESET_COL] = ''
                        settings[row][_MAPPING_NOTE_COL] = _NONE
                        settings[row][_MAPPING_NOTE_OFF_COL] = _NOTE_OFF_OFF
                    if self._save_mapping_settings():
                        self._set_trigger_options()
                elif sub_page == _SUB_PAGE_NOTE:
                    if _router.is_new_program:
                        _router.add_program(_NEW_PROGRAM)
                    row = id - _FIRST_NOTE
                    settings = self.mapping_settings
                    if row >= len(settings) or settings[row][_MAPPING_PRESET_COL] == '':
                        return
                    settings[row][_MAPPING_NOTE_COL] = value - 1 # 0 becomes _NONE
                    if self._save_mapping_settings():
                        self._set_note_options()
                elif sub_page == _SUB_PAGE_NOTE_OFF:
                    if _router.is_new_program:
                        _router.add_program(_NEW_PROGRAM)
                    row = id - _FIRST_NOTE_OFF
                    settings = self.mapping_settings
                    if row >= len(settings) or settings[row][_MAPPING_PRESET_COL] == '':
                        return
                    settings[row][_MAPPING_NOTE_OFF_COL] = value - 1 # 0 becomes _NONE
                    if self._save_mapping_settings():
                        self._set_note_off_options()
        elif sub_page == _SUB_PAGE_PROGRAM:
            if button_encoder_0 or button_encoder_1:
                return
            row = id - _FIRST_PROGRAM
            self.program_settings[row][1] = value - 1 # 0 becomes _NONE
            self._save_program_settings()
        else: # sub_page == _SUB_PAGE_BANKS
            if button_encoder_0 or button_encoder_1:
                return
            row = (id - _FIRST_BANK_MSB) // 2
            col = (id - _FIRST_BANK_MSB) % 2
            self.bank_settings[row][1][col] = value - 1 # 0 becomes _NONE
            self._save_bank_settings()

    def set_trigger(self) -> None:
        '''set active trigger (triggered by trigger button) at page level; called by ui.set_trigger (also calling router.set_trigger)'''
        sub_page = self.sub_page
        if not (sub_page == _SUB_PAGE_MAPPING or sub_page == _SUB_PAGE_NOTE or sub_page == _SUB_PAGE_NOTE_OFF):
            return
        self._load()

    def midi_learn(self, port: int, channel: int, note: int, program: int, cc: int, cc_value: int, route_number: int) -> None:
        '''process midi learn input, save settings and reload options; called by ui.process_midi_learn_data'''
        sub_page = self.sub_page
        block = self.selected_block
        _router = ui.router
        if sub_page == _SUB_PAGE_MAPPING or sub_page == _SUB_PAGE_NOTE or sub_page == _SUB_PAGE_NOTE_OFF:
            if block == _NAME:
                if program == _NONE or _router.active_program_number == program:
                    return
                _router.update(False, False, False, False, False, False, program)
            elif block == _INPUT_DEVICE:
                if route_number == _NONE:
                    return
                from_device = _router.input_devices_tuple_assigned.index(_router.routing[route_number]['input_device'])
                if from_device == _router.input_device_value:
                    return
                ui.ui.set_trigger(from_device)
            elif block == _INPUT_PRESET:
                if route_number == _NONE:
                    return
                from_preset = _router.input_presets_tuple.index(_router.routing[route_number]['input_preset'])
                if from_preset == _router.input_preset_value:
                    return
                ui.ui.set_trigger(preset=from_preset)
            elif sub_page == _SUB_PAGE_NOTE:
                if note == _NONE:
                    return
                row = block - _FIRST_NOTE
                settings = self.mapping_settings
                if row >= len(settings) or settings[row][_MAPPING_PRESET_COL] == '':
                    return
                settings[row][_MAPPING_NOTE_COL] = note
                if self._save_mapping_settings():
                    self._set_note_options()
        elif sub_page == _SUB_PAGE_PROGRAM:
            for i in range(_NR_OUT_PORTS):
                if block == _FIRST_PROGRAM + i:
                    self.program_settings[port][1] = program
                    if self._save_program_settings():
                        self._set_program_options()
                    return
        else: # sub_page == _SUB_PAGE_BANKS
            if cc == _CC_BANK_MSB:
                col = 0
            elif cc == _CC_BANK_LSB:
                col = 1
            else:
                return
            for i in range(_NR_OUT_PORTS):
                if col == 0 and block == _FIRST_BANK_MSB + 2 * i or col == 1 and block == _FIRST_BANK_LSB + 2 * i:
                    self.bank_settings[port][1][col] = cc_value
                    if self._save_bank_settings():
                        self._set_bank_options()
                    return

    def _build_page(self) -> None:
        '''build page (without drawing it); called by self.__init__ and self._build_sub_page'''
        sub_page = self.sub_page
        if sub_page is None or self.page_is_built:
            return
        self.page_is_built = True
        _build_sub_page = self._build_sub_page
        sub_pages_title_bars = self.sub_pages_title_bars
        sub_pages_blocks = self.sub_pages_blocks
        sub_pages_empty_blocks = self.sub_pages_empty_blocks
        for i in range(_SUB_PAGES):
            title_bar, blocks, empty_blocks = _build_sub_page(i)
            sub_pages_title_bars.append(title_bar)
            sub_pages_blocks.append(blocks)
            sub_pages_empty_blocks.append(empty_blocks)
        self._set_sub_page(sub_page)

    def _build_sub_page(self, sub_page: int) -> tuple:
        '''build sub-page (without drawing it); called by self._build_page'''
        if not self.page_is_built:
            self._build_page()
            return None, [], []
        blocks = []
        empty_blocks = []
        selected_block = self.selected_block
        _callback_input = self.callback_input
        if sub_page == _SUB_PAGE_MAPPING or sub_page == _SUB_PAGE_NOTE or sub_page == _SUB_PAGE_NOTE_OFF:
            if sub_page == _SUB_PAGE_MAPPING:
                title_bar = TitleBar('program: mapping', 1, _SUB_PAGES)
            elif sub_page == _SUB_PAGE_NOTE:
                title_bar = TitleBar('program: mapping note', 2, _SUB_PAGES)
            else: # sub_page == _SUB_PAGE_NOTE_OFF
                title_bar = TitleBar('program: mapping note off', 3, _SUB_PAGES)
            blocks.append(SelectBlock(_NAME, 0, 0, 2, selected_block == _NAME, 'program', callback_func=_callback_input))
            blocks.append(SelectBlock(_INPUT_DEVICE, 1, 0, 1, selected_block == _INPUT_DEVICE, 'input device', add_line=True,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_INPUT_PRESET, 1, 1, 1, selected_block == _INPUT_PRESET, 'input preset', add_line=True,
                                      callback_func=_callback_input))
            if sub_page == _SUB_PAGE_MAPPING:
                row = 1
                for i in range(_MAX_ROUTING_LAYERS):
                    row += 1
                    blocks.append(SelectBlock(_FIRST_OUTPUT_DEVICE + 2 * i, row, 0, 1, selected_block == _FIRST_OUTPUT_DEVICE + 2 * i,
                                            f'output device {i + 1}', callback_func=_callback_input))
                    blocks.append(SelectBlock(_FIRST_OUTPUT_PRESET + 2 * i, row, 1, 1, selected_block == _FIRST_OUTPUT_PRESET + 2 * i,
                                            f'output preset {i + 1}', callback_func=_callback_input))
            elif sub_page == _SUB_PAGE_NOTE:
                for i in range(_MAX_ROUTING_LAYERS):
                    blocks.append(SelectBlock(_FIRST_NOTE + i, 2 + i, 0, 2, selected_block == _FIRST_NOTE + i, '',
                                            callback_func=_callback_input))
            else: # sub_page == _SUB_PAGE_NOTE_OFF
                for i in range(_MAX_ROUTING_LAYERS):
                    blocks.append(SelectBlock(_FIRST_NOTE_OFF + i, 2 + i, 0, 2, selected_block == _FIRST_NOTE_OFF + i, '',
                                            callback_func=_callback_input))
        elif sub_page == _SUB_PAGE_PROGRAM:
            title_bar = TitleBar('program: program change', 4, _SUB_PAGES)
            for i in range(_NR_OUT_PORTS):
                blocks.append(SelectBlock(_FIRST_PROGRAM + i, i, 0, 2, selected_block == _FIRST_PROGRAM + i, '', _PROGRAM_CHANGE_OPTIONS,
                                          callback_func=_callback_input))
        else: # sub_page == _SUB_PAGE_BANKS
            title_bar = TitleBar('program: bank select', 5, _SUB_PAGES)
            for i in range(_NR_OUT_PORTS):
                blocks.append(SelectBlock(_FIRST_BANK_MSB + 2* i, i, 0, 1, selected_block == _FIRST_BANK_MSB + 2 * i, '',
                                          _BANK_SELECT_OPTIONS, callback_func=_callback_input))
                blocks.append(SelectBlock(_FIRST_BANK_LSB + 2 * i, i, 1, 1, selected_block == _FIRST_BANK_LSB + 2 * i, 'msb / lsb',
                                          _BANK_SELECT_OPTIONS, callback_func=_callback_input))
        return title_bar, blocks, empty_blocks

    def _load(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks; called by self.set_visibility, Page*.program_change, Page*.process_user_input
        and PageProgram.set_trigger'''
        if ui.ui.active_pop_up is not None:
            redraw = False
        self._set_mapping_options(False)
        self._set_program_options(False)
        self._set_bank_options(False)
        if redraw:
            self._draw()

    def _set_mapping_options(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks on mapping sub-page; called by self._load'''
        sub_page = self.sub_page
        if not (sub_page == _SUB_PAGE_MAPPING or sub_page == _SUB_PAGE_NOTE or sub_page == _SUB_PAGE_NOTE_OFF):
            return
        self.mapping_settings.clear()
        blocks = self.blocks
        _router = ui.router
        input_devices = _router.input_devices_tuple_assigned
        input_presets = _router.input_presets_tuple
        input_device_value = _router.input_device_value
        input_preset_value = _router.input_preset_value
        blocks[_NAME].set_options(ChainMapTuple(ui.data.programs_tuple, (_ADD_NEW_LABEL,)), _router.active_program_number, redraw)
        blocks[_INPUT_DEVICE].set_options(input_devices, input_device_value, redraw)
        blocks[_INPUT_PRESET].set_options(input_presets, input_preset_value, redraw)
        routing = _router.routing
        if len(routing) > 0:
            input_device = input_devices[input_device_value]
            input_preset = input_presets[input_preset_value]
            settings = self.mapping_settings
            for route in routing:
                if route['input_device'] == input_device and route['input_preset'] == input_preset:
                    settings.append([route['output_device'], route['output_preset'], route['note'], route['note_off']])
        if sub_page == _SUB_PAGE_MAPPING:
            self._set_trigger_options(redraw)
        elif sub_page == _SUB_PAGE_NOTE:
            self._set_note_options(redraw)
        else: # sub_page == _SUB_PAGE_NOTE_OFF
            self._set_note_off_options(redraw)

    def _set_trigger_options(self, redraw: bool = True) -> None:
        '''load and set options and values to trigger selection blocks on mapping sub-page; called by self.process_user_input and
        self._load'''
        _router = ui.router
        devices_tuple = ChainMapTuple(_EMPTY_OPTIONS_LONG, _router.output_devices_tuple_assigned)
        self.output_devices_tuple = devices_tuple
        settings = self.mapping_settings
        presets_tuples = _router.output_presets_tuples
        blocks = self.blocks
        for i, (output_device, output_preset, _, _) in enumerate(settings):
            if output_device == '':
                device = 0
                preset_tuple = _EMPTY_OPTIONS_LONG
            else:
                device = devices_tuple.index(output_device)
                preset_tuple = ChainMapTuple(_EMPTY_OPTIONS_LONG, presets_tuples[output_device])
            blocks[_FIRST_OUTPUT_DEVICE + 2 * i].set_options(devices_tuple, device, redraw)
            preset = 0 if output_preset == '' else preset_tuple.index(output_preset)
            blocks[_FIRST_OUTPUT_PRESET + 2 * i].set_options(preset_tuple, preset, redraw)
        if len(settings) < _MAX_ROUTING_LAYERS:
            for i in range(len(settings), _MAX_ROUTING_LAYERS):
                blocks[_FIRST_OUTPUT_DEVICE + 2 * i].set_options(devices_tuple, 0, redraw)
                blocks[_FIRST_OUTPUT_PRESET + 2 * i].set_options(_EMPTY_OPTIONS_LONG, 0, redraw)

    def _set_note_options(self, redraw: bool = True) -> None:
        '''load and set options and values to note blocks on mapping note sub-page; called by self.process_user_input, self.midi_learn
        and self._load'''
        settings = self.mapping_settings
        blocks = self.blocks
        for i, (output_device, output_preset, note, _) in enumerate(settings):
            device = 'n/a' if output_device == '' else output_device
            preset = 'n/a' if output_preset == '' else output_preset
            block = blocks[_FIRST_NOTE + i]
            label = f': {preset} - note'
            label = f'{device[0:_MAX_LABEL_LENGTH - len(label)]}{label}'
            block.set_label(label, False)
            block.set_options(_NOTE_OPTIONS, note + 1, redraw) # _NONE becomes 0
        if len(settings) < _MAX_ROUTING_LAYERS:
            for i in range(len(settings), _MAX_ROUTING_LAYERS):
                block = blocks[_FIRST_NOTE + i]
                block.set_label('n/a: n/a - note', False)
                block.set_options(_EMPTY_OPTIONS_SHORT, 0, redraw)

    def _set_note_off_options(self, redraw: bool = True) -> None:
        '''load and set options and values to note blocks on mapping note off sub-page; called by self.process_user_input and self._load'''
        settings = self.mapping_settings
        blocks = self.blocks
        for i, (output_device, output_preset, _, note_off) in enumerate(settings):
            device = 'n/a' if output_device == '' else output_device
            preset = 'n/a' if output_preset == '' else output_preset
            block = blocks[_FIRST_NOTE_OFF + i]
            label = f': {preset} - note off'
            label = f'{device[0:_MAX_LABEL_LENGTH - len(label)]}{label}'
            block.set_label(label, False)
            block.set_options(_NOTE_OFF_OPTIONS, note_off + 1, redraw) # _NONE becomes 0
        if len(settings) < _MAX_ROUTING_LAYERS:
            for i in range(len(settings), _MAX_ROUTING_LAYERS):
                block = blocks[_FIRST_NOTE_OFF + i]
                block.set_label('n/a: n/a - note off', False)
                block.set_options(_EMPTY_OPTIONS_LONG, 0, redraw)

    def _set_program_options(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks on program change sub-page; called by self.midi_learn and self._load'''
        if self.sub_page != _SUB_PAGE_PROGRAM:
            return
        _router = ui.router
        device_mapping = ui.data.output_device_mapping
        settings = self.program_settings
        program_change = _router.program['program_change']
        blocks = self.blocks
        for i in range(_NR_OUT_PORTS):
            settings[i][0] = ''
            settings[i][1] = _NONE
        for key, mapping in device_mapping.items():
            port = mapping['port']
            settings[port][0] = key
            try:
                settings[port][1] = program_change[key]
            except:
                settings[port][1] = _NONE
        for port, (device, program) in enumerate(settings):
            if device == '':
                label = f'p{port + 1} n/a'
                options = _EMPTY_OPTIONS_SHORT
            else:
                label = f'p{port + 1} {device}'
                options = _PROGRAM_CHANGE_OPTIONS
            block = blocks[_FIRST_PROGRAM + port]
            block.set_label(label, False)
            block.set_options(options, program + 1, redraw) # _NONE becomes 0

    def _set_bank_options(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks on bank select sub-page; called by self.midi_learn and self._load'''
        if self.sub_page != _SUB_PAGE_BANK:
            return
        _router = ui.router
        device_mapping = ui.data.output_device_mapping
        settings = self.bank_settings
        bank_select = _router.program['bank_select']
        blocks = self.blocks
        for i in range(_NR_OUT_PORTS):
            settings[i][0] = ''
            settings[i][1] = [_NONE, _NONE]
        for key, mapping in device_mapping.items():
            port = mapping['port']
            settings[port][0] = key
            try:
                bank = bank_select[key]
                settings[port][1] = [bank[0], bank[1]]
            except:
                settings[port][1] = [_NONE, _NONE]
        for port, (device, bank) in enumerate(settings):
            if device == '':
                label = f'p{port + 1} n/a'
                options = _EMPTY_OPTIONS_SHORT
            else:
                label = f'p{port + 1} {device}'
                options = _BANK_SELECT_OPTIONS
            block = blocks[_FIRST_BANK_MSB + 2 * port]
            block.set_label(label, False)
            block.set_options(options, bank[0] + 1, redraw) # _NONE becomes 0
            blocks[_FIRST_BANK_LSB + 2 * port].set_options(selection=bank[1] + 1, redraw=redraw) # _NONE becomes 0

    def _save_mapping_settings(self) -> bool:
        '''save values from input blocks on mapping sub-pages; called by self.process_user_input'''
        _router = ui.router
        routing = _router.routing
        input_devices = _router.input_devices_tuple_assigned
        input_triggers = _router.input_presets_tuple
        input_device = input_devices[_router.input_device_value] if len(input_devices) > 0 else ''
        input_preset_value = _router.input_preset_value
        input_preset = input_triggers[input_preset_value] if input_preset_value != _NONE and len(input_triggers) > 0 else ''
        changed = False
        settings = self.mapping_settings
        # check routing list for missing routes and add those
        for i, (output_device, output_preset, note, note_off) in enumerate(settings):
            if output_device == '':
                continue
            # skip if output preset is assigned twice (so it will not save, but it will also not remove the line)
            if output_preset != '':
                skip = False
                for j, (output_device_2, output_preset_2, _, _) in enumerate(settings):
                    if i == j or output_device != output_device_2:
                        continue
                    if output_preset == output_preset_2:
                        skip = True
                        break
                if skip:
                    return False
            found = False
            for route in routing:
                if route['input_device'] == input_device and route['input_preset'] == input_preset and \
                        route['output_device'] == output_device and route['output_preset'] == output_preset:
                    found = True
                    if route['note'] != note or route['note_off'] != note_off:
                        changed = True
                    break
            if found:
                continue
            new_route = {'input_device': input_device, 'input_preset': input_preset,
                'output_device': output_device, 'output_preset': output_preset, 'note': note, 'note_off': note_off}
            routing.append(new_route)
            changed = True
        # check routing list for removed routes and delete those
        for i in range(len(routing) - 1, -1, -1):
            route = routing[i]
            if route['input_device'] != input_device or route['input_preset'] != input_preset:
                continue
            found = False
            routing_output_device = route['output_device']
            routing_output_preset = route['output_preset']
            for settings_output_device, settings_output_preset, _, _ in settings:
                if routing_output_device == settings_output_device and routing_output_preset == settings_output_preset:
                    found = True
                    break
            if found:
                continue
            del routing[i]
            changed = True
        if changed:
            if not _router.program_changed:
                _router.program_changed = True
            _router.update(False, False, False, False, False, False)
        return changed

    def _save_program_settings(self) -> bool:
        '''save values from input blocks on program change sub-page; called by self.process_user_input and self.midi_learn'''
        _router = ui.router
        changed = False
        program_change = _router.program['program_change']
        for device, program in self.program_settings:
            if program == _NONE or device == '':
                continue
            found = device in program_change
            if not found or found and program_change[device] != program:
                changed = True
                program_change[device] = program
        if changed:
            if not _router.program_changed:
                _router.program_changed = True
            _router.update(False, False, False, False, False, False)
        return changed

    def _save_bank_settings(self) -> bool:
        '''save values from input blocks on bank select sub-page; called by self.process_user_input and self.midi_learn'''
        _router = ui.router
        changed = False
        bank_select = _router.program['bank_select']
        for device, bank in self.bank_settings:
            if bank == [_NONE, _NONE] or device == '':
                continue
            found = device in bank_select
            if not found or found and bank_select[device] != bank:
                if found: print(bank_select[device], '!=', bank, bank_select[device] != bank)
                changed = True
                bank_select[device] = [bank[0], bank[1]]
        if changed:
            if not _router.program_changed:
                _router.program_changed = True
            _router.update(False, False, False, False, False, False)
        return changed

    def _callback_text_edit(self, caller_id: int, text: str) -> None:
        '''callback function for text edit pop-up; called (passed on) by self._callback_menu'''
        if caller_id != _NAME or text == '' or self.program_name == text:
            return
        _router = ui.router
        if _router.is_new_program:
            _router.add_program(text)
        else:
            _router.rename_active_program(text)

    def _callback_confirm(self, caller_id: int, confirm: bool) -> None:
        '''callback for confirm pop-up; called (passed on) by self.process_user_input, self._callback_confirm and self._callback_menu'''
        sub_page = self.sub_page
        if sub_page == _SUB_PAGE_MAPPING:
            _router = ui.router
            if caller_id == _CONFIRM_DELETE:
                if not confirm:
                    return
                _router.delete_active_program()
            elif caller_id == _CONFIRM_SAVE:
                if confirm:
                    ui.ui.pop_ups[_POP_UP_CONFIRM].open(self, _CONFIRM_REPLACE,
                                                        f'replace {_router.active_program_number + 1:0>3}?', self._callback_confirm)
                else:
                    next_program = self.next_program
                    if next_program != _NONE:
                        _router.update(False, False, False, False, False, False, next_program)
            elif caller_id == _CONFIRM_REPLACE:
                _router.save_active_program(confirm)
                next_program = self.next_program
                if next_program != _NONE:
                    if not confirm and next_program > _router.active_program_number:
                        next_program += 1
                    _router.update(False, False, False, False, False, False, next_program)

    def _callback_menu(self, caller_id: int, selection: int) -> None:
        '''callback for menu pop-up; called (passed on) by self.process_user_input'''
        sub_page = self.sub_page
        if sub_page == _SUB_PAGE_MAPPING:
            if caller_id == _NAME:
                _router = ui.router
                program_changed = _router.program_changed
                if program_changed and selection == _SAVE_W:
                    self.next_program = _NONE
                    ui.ui.pop_ups[_POP_UP_CONFIRM].open(self, _CONFIRM_SAVE, 'save changes?', self._callback_confirm)
                elif program_changed and selection == _RENAME_W or not program_changed and selection == _RENAME_WO:
                    text = self.program_name
                    if text == _ADD_NEW_LABEL:
                        text = ''
                    ui.ui.pop_ups[_POP_UP_TEXT_EDIT].open(self, _NAME, text, callback_func=self._callback_text_edit)
                elif program_changed and selection == _MOVE_BACKWARD_W or not program_changed and selection == _MOVE_BACKWARD_WO:
                    destination = _router.active_program_number - 1
                    if destination >= 0:
                        _router.move_active_program(destination)
                    else:
                        _router.update(False, False, False, False, False, False)
                elif program_changed and selection == _MOVE_FORWARD_W or not program_changed and selection == _MOVE_FORWARD_WO:
                    destination = _router.active_program_number + 1
                    if destination < len(ui.data.routing_programs):
                        _router.move_active_program(destination)
                    else:
                        _router.update(False, False, False, False, False, False)
                else: # program_changed and selection == _MOVE_TO_W or not program_changed and selection == _MOVE_TO_WO
                    options = tuple(str(i) for i in range(len(ui.data.routing_programs)))
                    self._draw()
                    ui.ui.pop_ups[_POP_UP_SELECT].open(self, _SELECT_POSITION, 'move to:', options,
                                                       _router.active_program_number, callback_func=self._callback_select)

    def _callback_select(self, caller_id: int, selection: int) -> None:
        '''callback for select pop-up; called (passed on) by self._callback_menu'''
        if caller_id == _SELECT_POSITION:
            _router = ui.router
            if selection == _router.active_program_number:
                _router.update(False, False, False, False, False, False)
            else:
                _router.move_active_program(selection)