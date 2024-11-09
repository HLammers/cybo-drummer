''' Library providing input pages class for Cybo-Drummer - Humanize Those Drum Computers!
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
from ui_blocks import TitleBar, EmptyRow, EmptyBlock, SelectBlock

_NONE                    = const(-1)

_NR_IN_PORTS             = const(6)
_MAX_PRESETS             = const(6)

_CHANNEL_OPTIONS         = GenOptions(16, 1, ('__',), str)
_NOTE_OPTIONS            = GenOptions(128, first_options=('___',), func=mt.number_to_note)
_ADD_NEW_LABEL           = '[add new]'

_SUB_PAGES               = const(3)
_SUB_PAGE_PORTS          = const(0)
_SUB_PAGE_DEVICES        = const(1)
_SUB_PAGE_PRESETS        = const(2)

_SELECT_SUB_PAGE         = const(-1)
_PORT_FIRST_DEVICE       = const(0)
_PORT_FIRST_CHANNEL      = const(1)
_DEVICE_DEVICE           = const(0)
_DEVICE_TRIGGER          = const(1)
_DEVICE_TRIGGER_NOTE     = const(2)
_DEVICE_TRIGGER_PEDAL_CC = const(3)
_PRESET_DEVICE           = const(0)
_PRESET_PRESET           = const(1)
_PRESET_CC_MIN           = const(2)
_PRESET_CC_MAX           = const(3)
_PRESET_FIRST_MAP        = const(4)

_POP_UP_TEXT_EDIT        = const(0)
_POP_UP_CONFIRM          = const(3)

class PageInput(Page):
    '''input page class; initiated once by ui.__init__'''

    def __init__(self, id: int, x: int, y: int, w: int, h: int, visible: bool) -> None:
        super().__init__(id, x, y, w, h, visible)
        ###### only for testing or screenshot
        # self.sub_page = 2
        self.port_settings = [[_NONE, '']] * _NR_IN_PORTS
        self.device_device = 0
        self.device_device_name = ''
        self.device_new_device = False
        self.device_trigger = 0
        self.device_trigger_name = ''
        self.device_new_trigger = False
        self.preset_maps = [''] * _MAX_PRESETS
        self.preset_device = 0
        self.preset_device_name = ''
        self.preset_preset = 0
        self.preset_preset_name = ''
        self.preset_new_preset = False
        self.selected_port = _NONE
        self.selected_port_device = ''
        self.page_is_built = False
        self._build_page()

    def program_change(self) -> None:
        '''update page after program change (also needed to trigger draw); called by ui.program_change'''
        if self.visible:
            self._load()
        else:
            selected_block = self.selected_block
            blocks = self.blocks
            if selected_block != 0:
                blocks[selected_block].update(False, redraw=False)
                blocks[0].update(True, redraw=False)
            self.selected_block = 0

    def process_user_input(self, id: int, value: int = _NONE, text: str = '',
                           button_encoder_0: bool = False, button_encoder_1: bool = False) -> None:
        '''process user input at page level (ui.ui.set_user_input_dict > global user_input_dict > ui.process_user_input >
        Page/PagesTab.process_user_input); called by ui.process_user_input'''
        if id == _SELECT_SUB_PAGE:
            if button_encoder_0 or button_encoder_1 or value is None or value == self.sub_page:
                return
            self._set_sub_page(value)
            self._load()
            return
        sub_page = self.sub_page
        if sub_page == _SUB_PAGE_PORTS:
            if button_encoder_0 or button_encoder_1:
                return
            port = (id - _PORT_FIRST_DEVICE) // 2
            col = (id - _PORT_FIRST_DEVICE) % 2
            if col == 0: # channel
                self.port_settings[port][col] = _NONE if value == _NONE else value - 1 # value == 0 becomes _NONE
            else:        # device
                self.port_settings[port][col] = '' if text == '____' else text
            self.selected_port = port
            self._save_port_settings()
        elif sub_page == _SUB_PAGE_DEVICES:
            if button_encoder_0:
                if id == _DEVICE_DEVICE or id == _DEVICE_TRIGGER:
                    ui.ui.pop_ups[_POP_UP_CONFIRM].open(self, id, 'delete?', self._callback_confirm)
            elif button_encoder_1:
                if id == _DEVICE_DEVICE:
                    text = self.device_device_name
                    if text == _ADD_NEW_LABEL:
                        text = ''
                    ui.ui.pop_ups[_POP_UP_TEXT_EDIT].open(self, _DEVICE_DEVICE, text, callback_func=self._callback_text_edit)
                elif id == _DEVICE_TRIGGER:
                    text = self.device_trigger_name
                    if text == _ADD_NEW_LABEL:
                        text = ''
                    ui.ui.pop_ups[_POP_UP_TEXT_EDIT].open(self, _DEVICE_TRIGGER, text, callback_func=self._callback_text_edit)
            elif id == _DEVICE_DEVICE:
                if value == _NONE or value == self.device_device:
                    return
                self.device_device = value
                self.device_new_device = text == _ADD_NEW_LABEL
                self.device_trigger = 0
                self.device_new_trigger = self.device_new_device
                self._set_device_options()
            elif id == _DEVICE_TRIGGER:
                if value == _NONE or value == self.device_trigger:
                    return
                self.device_trigger = value
                self.device_new_trigger = text == _ADD_NEW_LABEL
                self._set_device_options()
            else: # device settings
                if value == _NONE or self.device_new_device or self.device_new_trigger:
                    return
                if self._save_device_settings(id, value):
                    self._set_device_options()
        else: #sub_page == _SUB_PAGE_PRESETS
            if button_encoder_0:
                if id == _PRESET_PRESET:
                    ui.ui.pop_ups[_POP_UP_CONFIRM].open(self, _PRESET_PRESET, 'delete?', self._callback_confirm)
            elif button_encoder_1:
                if id == _PRESET_PRESET:
                    text = self.preset_preset_name
                    if text == _ADD_NEW_LABEL:
                        text = ''
                    ui.ui.pop_ups[_POP_UP_TEXT_EDIT].open(self, _PRESET_PRESET, text, callback_func=self._callback_text_edit)
            elif id == _PRESET_DEVICE:
                if value == _NONE or value == self.preset_device:
                    return
                self.preset_device = value
                ui.ui.set_trigger(value)
            elif id == _PRESET_PRESET:
                if value == _NONE or value == self.preset_preset:
                    return
                self.preset_preset = value
                ui.ui.set_trigger(preset=value)
            else: # preset settings
                if value == _NONE or self.preset_new_preset:
                    return
                if self._save_preset_settings(id, value, text):
                    self._set_preset_options()

    def set_trigger(self) -> None:
        '''set active trigger (triggered by trigger button) at page level; called by ui.set_trigger (also calling router.set_trigger)'''
        if self.sub_page != _SUB_PAGE_PRESETS:
            return
        self.preset_new_preset = ui.router.input_preset_value != self.preset_preset
        self._load_preset_options()

    def midi_learn(self, port: int, channel: int, note: int, program: int, cc: int, cc_value: int, route_number: int) -> None:
        '''process midi learn input, save settings and reload options; called by ui.process_midi_learn_data'''
        sub_page = self.sub_page
        block = self.selected_block
        if sub_page == _SUB_PAGE_PORTS:
            if channel == _NONE and route_number == _NONE:
                return
            port = (block - _PORT_FIRST_DEVICE) // 2
            col = (block - _PORT_FIRST_DEVICE) % 2
            if col == 1: # device
                return
            self.port_settings[port][col] = channel + 1
            if self._save_port_settings():
                self._set_port_options()
        elif sub_page == _SUB_PAGE_DEVICES:
            if block == _DEVICE_DEVICE:
                if route_number == _NONE:
                    return
                _router = ui.router
                from_device = _router.input_devices_tuple_assigned.index(_router.routing[route_number]['input_device'])
                if from_device == _router.input_device_value:
                    return
                self.device_device = from_device + 1
                self.device_new_device = False
                self.device_trigger = 0
                self.device_new_trigger = False
                self._set_device_options()
            elif block == _DEVICE_TRIGGER_NOTE:
                if note == _NONE or self.device_new_device or self.device_new_trigger:
                    return
                if self._save_device_settings(block, note):
                    self._set_device_options()
            elif block == _DEVICE_TRIGGER_PEDAL_CC:
                if note == _NONE or self.device_new_device or self.device_new_trigger:
                    return
                if self._save_device_settings(_DEVICE_TRIGGER_PEDAL_CC, cc):
                    self._set_device_options()
        elif sub_page == _SUB_PAGE_PRESETS:
            if block == _PRESET_DEVICE:
                if route_number == _NONE:
                    return
                _router = ui.router
                from_device = _router.input_devices_tuple_assigned.index(_router.routing[route_number]['input_device'])
                if from_device == self.preset_device:
                    return
                self.preset_device = from_device
                ui.ui.set_trigger(from_device)
            elif block == _PRESET_PRESET:
                if route_number == _NONE:
                    return
                _router = ui.router
                from_preset = _router.input_presets_tuple.index(_router.routing[route_number]['input_preset'])
                if from_preset == self.preset_preset:
                    return
                self.preset_preset = from_preset
                ui.ui.set_trigger(preset=from_preset)
            elif block == _PRESET_CC_MIN or block == _PRESET_CC_MAX:
                if cc_value == _NONE or self.preset_new_preset:
                    return
                if self._save_preset_settings(block, cc_value, ''):
                    self._set_preset_options()

    def _build_page(self) -> None:
        '''build page (without drawing it); called by self.__init__ and self._build_sub_page'''
        if self.page_is_built:
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
        self._set_sub_page(self.sub_page)

    def _build_sub_page(self, sub_page: int) -> tuple:
        '''build sub-page (without drawing it); called by self._build_page'''
        if not self.page_is_built:
            self._build_page()
            return None, [], []
        blocks = []
        empty_blocks = []
        selected_block = self.selected_block
        _callback_input = self.callback_input
        if sub_page == _SUB_PAGE_PORTS:
            title_bar = TitleBar('input ports', 1, _SUB_PAGES)
            row = -1
            for i in range(_NR_IN_PORTS):
                row += 1
                blocks.append(SelectBlock(_PORT_FIRST_DEVICE + 2 * i, row, 0, 1, selected_block == _PORT_FIRST_DEVICE + 2 * i,
                                          f'p{i + 1} device', callback_func=_callback_input))
                blocks.append(SelectBlock(_PORT_FIRST_CHANNEL + 2 * i, row, 1, 1, selected_block == _PORT_FIRST_CHANNEL + 2 * i,
                                          f'p{i + 1} channel', _CHANNEL_OPTIONS, callback_func=_callback_input))
        elif sub_page == _SUB_PAGE_DEVICES:
            title_bar = TitleBar('input devices/triggers', 2, _SUB_PAGES)
            blocks.append(SelectBlock(_DEVICE_DEVICE, 0, 0, 1, selected_block == _DEVICE_DEVICE, 'input device', add_line=True,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_DEVICE_TRIGGER, 0, 1, 1, selected_block == _DEVICE_TRIGGER, 'input trigger', add_line=True,
                                      callback_func=_callback_input))
            empty_blocks.append(EmptyBlock(_NONE, 1, 0, 1))
            blocks.append(SelectBlock(_DEVICE_TRIGGER_NOTE, 1, 1, 1, selected_block == _DEVICE_TRIGGER_NOTE, 'note', _NOTE_OPTIONS,
                                      callback_func=_callback_input))
            empty_blocks.append(EmptyBlock(_NONE, 2, 0, 1))
            blocks.append(SelectBlock(_DEVICE_TRIGGER_PEDAL_CC, 2, 1, 1, selected_block == _DEVICE_TRIGGER_PEDAL_CC, 'pedal cc',
                                      _CHANNEL_OPTIONS, callback_func=_callback_input))
            empty_blocks.append(EmptyRow(_NONE, 3))
            empty_blocks.append(EmptyRow(_NONE, 4))
            empty_blocks.append(EmptyRow(_NONE, 5))
        else: # sub_page == _SUB_PAGE_PRESETS:
            title_bar = TitleBar('input presets', 3, _SUB_PAGES)
            blocks.append(SelectBlock(_PRESET_DEVICE, 0, 0, 1, selected_block == _PRESET_DEVICE, 'input device', add_line=True,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_PRESET_PRESET, 0, 1, 1, selected_block == _PRESET_PRESET, 'input preset', add_line=True,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_PRESET_CC_MIN, 1, 0, 1, selected_block == _PRESET_CC_MIN, 'pedal cc min', _CHANNEL_OPTIONS,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_PRESET_CC_MAX, 1, 1, 1, selected_block == _PRESET_CC_MAX, 'pedal cc max', _CHANNEL_OPTIONS,
                                      callback_func=_callback_input))
            row = 1.5
            for i in range(_MAX_PRESETS):
                row += 0.5
                blocks.append(SelectBlock(_PRESET_FIRST_MAP + i, int(row), int(i & 1), 1, selected_block == _PRESET_FIRST_MAP + i,
                                          f'trigger {i + 1}', callback_func=_callback_input))
            empty_blocks.append(EmptyRow(_NONE, 5))
        return title_bar, blocks, empty_blocks

    def _load(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks; called by self.set_visibility, Page*.program_change and Page*.process_user_input'''
        if ui.ui.active_pop_up is not None:
            redraw = False
        self._load_port_options()
        self._set_device_options(False)
        self._load_preset_options(False)
        if redraw:
            self._draw()

    def _load_port_options(self) -> None:
        '''load and set values to input blocks on ports sub-page; called by self._load'''
        settings = self.port_settings
        for i in range(_NR_IN_PORTS):
            settings[i] = [_NONE, '']
        for device, map in ui.data.input_device_mapping.items():
            # settings[map['port']] = [map['channel'], device]
            port = map['port']
            if port != _NONE:
                settings[port] = [map['channel'], device]
        self._set_port_options(False)

    def _load_preset_options(self, redraw: bool = True) -> None:
        '''load and set values to options and values to input blocks on preset sub-page; called by self.set_trigger and self._load'''
        if self.preset_new_preset:
            preset_preset_name = _ADD_NEW_LABEL
            n = 0
        else:
            _router = ui.router
            input_devices = _router.input_devices_tuple_all
            preset_device_name = '' if len(input_devices) == 0 else input_devices[self.preset_device]
            self.preset_device_name = preset_device_name
            preset_preset = self.preset_preset
            presets_tuple = () if preset_device_name == '' else _router.input_presets_tuples[preset_device_name]
            if preset_preset < len(presets_tuple):
                preset_preset_name = presets_tuple[preset_preset]
                presets = ui.data.input_presets[preset_device_name]
                if preset_preset_name in presets:
                    maps = presets[preset_preset_name]['maps']
                    n = len(maps)
                else:
                    preset_preset_name = _ADD_NEW_LABEL
                    n = 0
            else:
                preset_preset_name = _ADD_NEW_LABEL
                n = 0
        self.preset_preset_name = preset_preset_name
        preset_maps = self.preset_maps
        for i in range(_MAX_PRESETS):
            preset_maps[i] = maps[i] if i < n else ''
        self._set_preset_options(redraw)

    def _set_port_options(self, redraw: bool = True) -> None:
        '''set options and values to input blocks on ports sub-page; called by self.process_user_input, self.midi_learn and
        self._load_port_options'''
        if self.sub_page != _SUB_PAGE_PORTS:
            return
        devices_tuple = ChainMapTuple(('____',), ui.router.input_devices_tuple_assigned)
        blocks = self.blocks
        selected_port = self.selected_port
        self.selected_port = _NONE
        for port, (channel, device) in enumerate(self.port_settings):
            if port == _NR_IN_PORTS:
                break
            if port == selected_port:
                device = self.selected_port_device
            device_option = 0 if device == '' else devices_tuple.index(device)
            blocks[_PORT_FIRST_DEVICE + 2 * port].set_options(devices_tuple, device_option, redraw)
            channel_option = channel + 1 # _NONE becomes 0
            blocks[_PORT_FIRST_CHANNEL + 2 * port].set_options(selection=channel_option, redraw=redraw)

    def _set_device_options(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks on device sub-page; called by self.process_user_input, self.midi_learn, self._load
        and self._callback_confirm'''
        if self.sub_page != _SUB_PAGE_DEVICES:
            return
        _router = ui.router
        devices_tuple = ChainMapTuple(_router.input_devices_tuple_all, (_ADD_NEW_LABEL,))
        if len(devices_tuple) == 1:
            self.device_new_device = True
        if self.device_new_device:
            self.device_device_name = _ADD_NEW_LABEL
            triggers_tuple = (_ADD_NEW_LABEL,)
            self.device_trigger_name = _ADD_NEW_LABEL
            note = 0
            pedal_cc = 0
        else:
            device_device_name = str(devices_tuple[self.device_device])
            self.device_device_name = device_device_name
            if self.device_new_trigger:
                triggers_tuple = (_ADD_NEW_LABEL,)
                self.device_trigger_name = _ADD_NEW_LABEL
                note = 0
                pedal_cc = 0
            else:
                triggers_tuple = ChainMapTuple(_router.input_triggers_tuples[device_device_name], (_ADD_NEW_LABEL,))
                device_trigger_name = str(triggers_tuple[self.device_trigger])
                self.device_trigger_name = device_trigger_name
                mapping = ui.data.input_devices[device_device_name]['mapping'][device_trigger_name]
                note = mapping['note'] + 1 # _NONE becomes 0
                pedal_cc = mapping['pedal_cc'] + 1 # _NONE becomes 0
        blocks = self.blocks
        blocks[_DEVICE_DEVICE].set_options(devices_tuple, self.device_device, redraw)
        blocks[_DEVICE_TRIGGER].set_options(triggers_tuple, self.device_trigger, redraw)
        blocks[_DEVICE_TRIGGER_NOTE].set_options(selection=note, redraw=redraw)
        blocks[_DEVICE_TRIGGER_PEDAL_CC].set_options(selection=pedal_cc, redraw=redraw)

    def _set_preset_options(self, redraw: bool = True) -> None:
        '''set options and values to input blocks on preset sub-page; called by self.process_user_input, self.midi_learn,
        self._load_preset_option and self._callback_confirm'''
        if self.sub_page != _SUB_PAGE_PRESETS:
            return
        _router = ui.router
        preset_device_name = self.preset_device_name
        presets_tuples = _router.input_presets_tuples
        if preset_device_name not in presets_tuples:
            self.preset_preset = 0
            presets_tuple = (_ADD_NEW_LABEL,)
            cc_min = 0
            cc_max = 0
        else:
            presets_tuple = ChainMapTuple(presets_tuples[preset_device_name], (_ADD_NEW_LABEL,))
            settings = ui.data.input_presets[preset_device_name][self.preset_preset_name]
            cc_min = settings['cc_min'] + 1 # _NONE becomes 0
            cc_max = settings['cc_max'] + 1 # _NONE becomes 0
        blocks = self.blocks
        blocks[_PRESET_DEVICE].set_options(_router.input_devices_tuple_all, self.preset_device, redraw)
        blocks[_PRESET_PRESET].set_options(presets_tuple, self.preset_preset, redraw)
        blocks[_PRESET_CC_MIN].set_options(selection=cc_min, redraw=redraw)
        blocks[_PRESET_CC_MAX].set_options(selection=cc_max, redraw=redraw)
        triggers_tuple = ChainMapTuple(('____',), _router.input_triggers_tuple)
        clear = self.preset_preset_name == _ADD_NEW_LABEL
        preset_maps = self.preset_maps
        for i in range(_MAX_PRESETS):
            if clear:
                preset_maps[i] = ''
            value = 0 if preset_maps[i] == '' else triggers_tuple.index(preset_maps[i])
            blocks[_PRESET_FIRST_MAP + i].set_options(triggers_tuple, value, redraw)

    def _save_port_settings(self) -> None:
        '''save values from input blocks on ports sub-page; called by self.process_user_input and self.midi_learn'''
        _data = ui.data
        mapping = _data.input_device_mapping
        changed = False
        selected_port = self.selected_port
        assigned_devices = []
        for device, definition in mapping.items():
            if definition['port'] != _NONE:
                assigned_devices.append(device)
        changed = False
        for port, (channel, device) in enumerate(self.port_settings):
            if port == selected_port:
                selected_port_device = device
                continue
            if device == '':
                continue
            if device in mapping:
                assigned_devices.remove(device)
                if mapping[device]['port'] != port:
                    mapping[device]['port'] = port
                    changed = True
            else:
                mapping[device] = {'port': port, 'channel': _NONE}
                changed = True
            if mapping[device]['channel'] != channel:
                mapping[device]['channel'] = channel
                changed = True
        for device in assigned_devices:
            mapping[device]['port'] = _NONE
            changed = True
        # do not save if selected port is set to an already assigned device
        if selected_port_device != '' and mapping[selected_port_device]['port'] == _NONE:
            mapping[selected_port_device] = {'port': selected_port}
            changed = True
        self.selected_port_device = selected_port_device
        if not changed:
            return
        _data.save_data_json_file()
        ui.router.update(False, False, False, False, False, False)

    def _save_device_settings(self, id: int, value: int) -> bool:
        '''save values from input blocks on device sub-page; called by self.process_user_input and self.midi_learn'''
        _data = ui.data
        changed = False
        device_key = self.device_device_name
        trigger_key = self.device_trigger_name
        devices = _data.input_devices
        if not device_key in devices:
            devices[device_key] = {'mapping': {}}
            changed = True
        mapping = devices[device_key]['mapping']
        if not trigger_key in mapping:
            mapping[trigger_key] = {'note': _NONE, 'pedal_cc': _NONE}
            changed = True
        trigger = mapping[trigger_key]
        if id == _DEVICE_TRIGGER_NOTE:
            key = 'note'
        else:
            key = 'pedal_cc'
        if trigger[key] != value:
            trigger[key] = value # 0 becomes _NONE
            changed = True
        if changed:
            ui.router.update(False, False, False, False, False, False)
            _data.save_data_json_file()
        return changed

    def _save_preset_settings(self, id: int, value: int, text: str) -> bool:
        '''save values from input blocks on preset sub-page; called by self.process_user_input and self.midi_learn'''
        _data = ui.data
        changed = False
        device_key = self.preset_device_name
        preset_key = self.preset_preset_name
        presets = _data.input_presets
        if not device_key in presets:
            presets[device_key] = {}
            changed = True
        if not preset_key in presets[device_key]:
            presets[device_key][preset_key] = {'maps': [], 'cc_min': _NONE, 'cc_max': _NONE}
            changed = True
        device = presets[device_key][preset_key]
        if id == _PRESET_CC_MIN or id == _PRESET_CC_MAX:
            key = 'cc_min' if id == _PRESET_CC_MIN else 'cc_max'
            if device[key] != value:
                device[key] = value # 0 becomes _NONE
                changed = True
        else: # maps
            preset_maps = self.preset_maps
            map_nr = id - _PRESET_FIRST_MAP
            store_text = '' if value == 0 else text
            preset_maps[map_nr] = store_text
            maps = []
            for map in preset_maps:
                if map != '' and map not in maps:
                    maps.append(map)
            device_maps = device['maps']
            if len(maps) != len(device_maps):
                changed = True
            else:
                for i, map in enumerate(device_maps):
                    if map != maps[i]:
                        changed = True
                        break
            if changed:
                for i in range(min(len(device_maps), len(maps))):
                    if device_maps[i] != maps[i]:
                        device_maps[i] = maps[i]
                while len(device_maps) > len(maps):
                    del device_maps[-1]
                while len(maps) > len(device_maps):
                    device_maps.append(maps[len(device_maps)])
        if changed:
            _data.save_data_json_file()
            ui.router.update(False, False, False, False, False, False)
        return changed

    def _callback_text_edit(self, caller_id: int, text: str) -> None:
        '''callback function for text edit pop-up; called (passed on) by self.process_user_input'''
        if text == '':
            return
        sub_page = self.sub_page
        if sub_page == _SUB_PAGE_DEVICES:
            if caller_id == _DEVICE_DEVICE:
                if self.device_device_name == text:
                    return
                if self.device_device_name == _ADD_NEW_LABEL:
                    self.device_new_device = False
                    ui.router.add_device(text, True)
                else:
                    ui.router.rename_device(self.device_device_name, text, True)
            elif caller_id == _DEVICE_TRIGGER:
                if self.device_trigger_name == text:
                    return
                if self.device_trigger_name == _ADD_NEW_LABEL:
                    self.device_new_trigger = False
                    ui.router.add_trigger(self.device_device_name, text, True)
                else:
                    ui.router.rename_trigger(self.device_device_name, self.device_trigger_name, text, True)
        elif sub_page == _SUB_PAGE_PRESETS and caller_id == _PRESET_PRESET:
            if self.preset_preset_name == text:
                return
            if self.preset_preset_name == _ADD_NEW_LABEL:
                self.preset_new_preset = False
                ui.router.add_preset(self.preset_device_name, text, True)
            else:
                ui.router.rename_preset(self.preset_device_name, self.preset_preset_name, text, True)

    def _callback_confirm(self, caller_id: int, confirm: bool) -> None:
        '''callback for confirm pop-up; called (passed on) by self.process_user_input'''
        if not confirm:
            return
        if caller_id == _DEVICE_DEVICE:
            ui.router.delete_device(self.device_device_name, True)
            if self.device_device > 0:
                self.device_device -= 1
            self._set_device_options()
        elif caller_id == _DEVICE_TRIGGER:
            ui.router.delete_trigger(self.device_device_name, self. device_trigger_name, True)
            if self.device_trigger > 0:
                self.device_trigger -= 1
            self._set_device_options()
        elif id == _PRESET_PRESET:
            ui.router.delete_preset(self.preset_device_name, self.preset_preset_name, True)
            if self.preset_preset > 0:
                self.preset_preset -= 1
            self._set_preset_options()