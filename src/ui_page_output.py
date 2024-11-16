''' Library providing output pages class for Cybo-Drummer - Humanize Those Drum Computers!
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

_NONE                  = const(-1)

_NR_OUT_PORTS          = const(6)
_MAX_PRESETS           = const(5)

_ON_OFF_OPTIONS        = ('off', 'on')
_CHANNEL_OPTIONS       = GenOptions(16, 1, ('__',), str)
_NOTE_OPTIONS          = GenOptions(128, first_options=('___',), func=mt.number_to_note)
_NOTE_OFF_OPTIONS      = GenOptions(922, 80, ('off', 'pulse', 'toggle'), str, ' ms')
_VELOCITY_OPTIONS      = GenOptions(127, func=str)
_CURVE_OPTIONS         = ('negative 3', 'negative 2', 'negative 1', 'linear', 'positive 1', 'positive 2', 'positive 3')

_NOTE_OFF_OFF          = const(-1) 

_ADD_NEW_LABEL         = '[add new]'

_SUB_PAGES             = const(4)
_SUB_PAGE_PORTS        = const(0)
_SUB_PAGE_DEVICES      = const(1)
_SUB_PAGE_TRIGGERS     = const(2)
_SUB_PAGE_PRESETS      = const(3)

_SELECT_SUB_PAGE       = const(-1)
_PORT_FIRST_DEVICE     = const(0)
_DEVICE_DEVICE         = const(0)
_DEVICE_CHANNEL        = const(1)
_DEVICE_0_NOTE_OFF     = const(2)
_DEVICE_RUNNING_STATUS = const(3)
_TRIGGER_DEVICE        = const(0)
_TRIGGER_TRIGGER       = const(1)
_TRIGGER_CHANNEL       = const(2)
_TRIGGER_NOTE          = const(3)
_TRIGGER_NOTE_OFF      = const(4)
_TRIGGER_THRESHOLD     = const(5)
_TRIGGER_CURVE         = const(6)
_TRIGGER_MIN_VELOCITY  = const(7)
_TRIGGER_MAX_VELOCITY  = const(8)
_PRESET_DEVICE         = const(0)
_PRESET_PRESET         = const(1)
_PRESET_FIRST_MAP      = const(2)
_PRESET_FIRST_NOTE     = const(3)

_POP_UP_TEXT_EDIT      = const(0)
_POP_UP_CONFIRM        = const(3)

class PageOutput(Page):
    '''output page class; initiated once by ui.__init__'''

    def __init__(self, id: int, x: int, y: int, w: int, h: int, visible: bool) -> None:
        super().__init__(id, x, y, w, h, visible)
        ###### only for testing or screenshot
        # self.sub_page = 3
        self.port_settings = [''] * _NR_OUT_PORTS
        self.device_device = 0
        self.device_device_name = ''
        self.device_new_device = False
        self.trigger_device = 0
        self.trigger_device_name = ''
        self.trigger_trigger = 0
        self.trigger_trigger_name = ''
        self.trigger_new_trigger = False
        self.preset_maps = [['', _NONE] for _ in range(_MAX_PRESETS)]
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
            if button_encoder_0 or button_encoder_1 or value == _NONE or value == self.sub_page:
                return
            self._set_sub_page(value)
            self._load()
            return
        sub_page = self.sub_page
        if sub_page == _SUB_PAGE_PORTS:
            if button_encoder_0 or button_encoder_1:
                return
            port = id - _PORT_FIRST_DEVICE
            self.port_settings[port] = '' if text == '____' else text # type: ignore
            self.selected_port = port
            self._save_port_settings()
        elif sub_page == _SUB_PAGE_DEVICES:
            if button_encoder_0:
                if id == _DEVICE_DEVICE:
                    ui.ui.pop_ups[_POP_UP_CONFIRM].open(self, _DEVICE_DEVICE, 'delete?', self._callback_confirm)
            elif button_encoder_1:
                if id == _DEVICE_DEVICE:
                    text = self.device_device_name
                    if text == _ADD_NEW_LABEL:
                        text = ''
                    ui.ui.pop_ups[_POP_UP_TEXT_EDIT].open(self, _DEVICE_DEVICE, text, callback_func=self._callback_text_edit)
            elif id == _DEVICE_DEVICE:
                if value == _NONE or value == self.device_device:
                    return
                self.device_device = value
                self.device_new_device = text == _ADD_NEW_LABEL
                self._set_device_options()
            else: # device settings
                if value == _NONE or self.device_new_device:
                    return
                if self._save_device_settings(id, value):
                    self._set_device_options()
        elif sub_page == _SUB_PAGE_TRIGGERS:
            if button_encoder_0:
                if id == _TRIGGER_TRIGGER:
                    ui.ui.pop_ups[_POP_UP_CONFIRM].open(self, _TRIGGER_TRIGGER, 'delete?', self._callback_confirm)
            elif button_encoder_1:
                if id == _TRIGGER_TRIGGER:
                    text = self.trigger_trigger_name
                    if text == _ADD_NEW_LABEL:
                        text = ''
                    ui.ui.pop_ups[_POP_UP_TEXT_EDIT].open(self, _TRIGGER_TRIGGER, text, callback_func=self._callback_text_edit)
            elif id == _TRIGGER_DEVICE:
                if value == _NONE or value == self.trigger_device:
                    return
                self.trigger_device = value
                self.trigger_trigger = 0
                self._set_trigger_options()
            elif id == _TRIGGER_TRIGGER:
                if value == _NONE or value == self.trigger_trigger:
                    return
                self.trigger_trigger = value
                self.trigger_new_trigger = text == _ADD_NEW_LABEL
                self._set_trigger_options()
            else: # device settings
                if value == _NONE or self.trigger_new_trigger:
                    return
                if self._save_trigger_settings(id, value):
                    self._set_trigger_options()
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
                self.preset_new_preset = False
                self._load_preset_options()
            elif id == _PRESET_PRESET:
                if value == _NONE or value == self.preset_preset:
                    return
                self.preset_preset = value
                self.preset_new_preset = False
                self._load_preset_options()
            else: # preset maps
                if value == _NONE or self.preset_new_preset:
                    return
                if self._save_preset_settings(id, value, text):
                    self._set_preset_options()

    def midi_learn(self, port: int, channel: int, note: int, program: int, cc: int, cc_value: int, route_number: int) -> None:
        '''process midi learn input, save settings and reload options; called by ui.process_midi_learn_data'''
        sub_page = self.sub_page
        block = self.selected_block
        if sub_page == _SUB_PAGE_DEVICES:
            if block == _DEVICE_CHANNEL:
                if channel == _NONE or self.device_new_device:
                    return
                value = channel + 1
            else:
                return
        elif sub_page == _SUB_PAGE_TRIGGERS:
            if block == _TRIGGER_CHANNEL:
                if channel == _NONE or self.trigger_new_trigger:
                    return
                value = channel + 1
            elif block == _TRIGGER_NOTE:
                if note == _NONE or self.trigger_new_trigger:
                    return
                value = note
            else:
                return
        elif sub_page == _SUB_PAGE_PRESETS:
            if block == _PRESET_DEVICE:
                if route_number == _NONE:
                    return
                _router = ui.router
                value = _router.output_devices_tuple_assigned.index(_router.routing[route_number]['output_device'])
            elif block == _PRESET_PRESET:
                if route_number == _NONE:
                    return
                _router = ui.router
                value = _router.output_presets_tuples[self.device_device_name].index(_router.routing[route_number]['output_preset'])
            elif _PRESET_FIRST_NOTE <= block <= _PRESET_FIRST_NOTE + 2 * _MAX_PRESETS:
                if note == _NONE or (block - _PRESET_FIRST_MAP) % 2 == 0:
                    return
                value = note
            else:
                return
        else:
            return
        self.blocks[block].set_selection(value)

    def _build_page(self) -> None:
        '''build page (without drawing it); called by self.__init__ and self._build_sub_page'''
        if self.sub_page is None or self.page_is_built:
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
            title_bar = TitleBar('output ports', 1, _SUB_PAGES)
            for i in range(_NR_OUT_PORTS):
                blocks.append(SelectBlock(_PORT_FIRST_DEVICE + i, i, 0, 2, selected_block == _PORT_FIRST_DEVICE + i,
                                          f'p{i + 1} device', callback_func=_callback_input))
        elif sub_page == _SUB_PAGE_DEVICES:
            title_bar = TitleBar('output devices', 2, _SUB_PAGES)
            blocks.append(SelectBlock(_DEVICE_DEVICE, 0, 0, 2, selected_block == _DEVICE_DEVICE, 'output device', add_line=True,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_DEVICE_CHANNEL, 1, 0, 2, selected_block == _DEVICE_CHANNEL, 'channel', _CHANNEL_OPTIONS,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_DEVICE_0_NOTE_OFF, 2, 0, 2, selected_block == _DEVICE_0_NOTE_OFF, '0 velocity as note off',
                                      _ON_OFF_OPTIONS, callback_func=_callback_input))
            blocks.append(SelectBlock(_DEVICE_RUNNING_STATUS, 3, 0, 2, selected_block == _DEVICE_RUNNING_STATUS, 'running status',
                                      _ON_OFF_OPTIONS, callback_func=_callback_input))
            empty_blocks.append(EmptyRow(_NONE, 4))
            empty_blocks.append(EmptyRow(_NONE, 5))
        elif sub_page == _SUB_PAGE_TRIGGERS:
            title_bar = TitleBar('output triggers', 3, _SUB_PAGES)
            blocks.append(SelectBlock(_TRIGGER_DEVICE, 0, 0, 1, selected_block == _TRIGGER_DEVICE, 'output device', add_line=True,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_TRIGGER_TRIGGER, 0, 1, 1, selected_block == _TRIGGER_TRIGGER, 'output trigger', add_line=True,
                                      callback_func=_callback_input))
            empty_blocks.append(EmptyBlock(_NONE, 1, 0, 1))
            blocks.append(SelectBlock(_TRIGGER_CHANNEL, 1, 1, 1, selected_block == _TRIGGER_CHANNEL, 'channel', _CHANNEL_OPTIONS,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_TRIGGER_NOTE, 2, 0, 1, selected_block == _TRIGGER_NOTE, 'note', _NOTE_OPTIONS,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_TRIGGER_NOTE_OFF, 2, 1, 1, selected_block == _TRIGGER_NOTE_OFF, 'note off', _NOTE_OFF_OPTIONS,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_TRIGGER_THRESHOLD, 3, 0, 1, selected_block == _TRIGGER_THRESHOLD, 'vel threshold', _VELOCITY_OPTIONS,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_TRIGGER_CURVE, 3, 1, 1, selected_block == _TRIGGER_CURVE, 'velocity curve', _CURVE_OPTIONS,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_TRIGGER_MIN_VELOCITY, 4, 0, 1, selected_block == _TRIGGER_MIN_VELOCITY, 'min velocity',
                                      _VELOCITY_OPTIONS, callback_func=_callback_input))
            blocks.append(SelectBlock(_TRIGGER_MAX_VELOCITY, 4, 1, 1, selected_block == _TRIGGER_MAX_VELOCITY, 'max velocity',
                                      _VELOCITY_OPTIONS, callback_func=_callback_input))
            empty_blocks.append(EmptyRow(_NONE, 5))
        else: # sub_page == _SUB_PAGE_PRESETS:
            title_bar = TitleBar('output presets', 4, _SUB_PAGES)
            blocks.append(SelectBlock(_PRESET_DEVICE, 0, 0, 1, selected_block == _PRESET_DEVICE, 'output device', add_line= True,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_PRESET_PRESET, 0, 1, 1, selected_block == _PRESET_PRESET, 'output preset', add_line=True,
                                      callback_func=_callback_input))
            row = 0
            for i in range(_MAX_PRESETS):
                row += 1
                blocks.append(SelectBlock(_PRESET_FIRST_MAP + 2 * i, row, 0, 1, selected_block == _PRESET_FIRST_MAP + 2 * i,
                                          f'trigger {i + 1}', callback_func=_callback_input))
                blocks.append(SelectBlock(_PRESET_FIRST_NOTE + 2 * i, row, 1, 1, selected_block == _PRESET_FIRST_NOTE + 2 * i,
                                          f'note', callback_func=_callback_input))
        return title_bar, blocks, empty_blocks

    def _load(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks; called by self.set_visibility, Page*.program_change and
        Page*.process_user_input'''
        if ui.ui.active_pop_up is not None:
            redraw = False
        self._load_port_options()
        self._set_device_options(False)
        self._set_trigger_options(False)
        self._load_preset_options(False)
        if redraw:
            self._draw()

    def _load_port_options(self) -> None:
        '''load and set values to input blocks on ports sub-page; called by self._load'''
        settings = self.port_settings
        for i in range(_NR_OUT_PORTS):
            settings[i] = ''
        for device, map in ui.data.output_device_mapping.items():
            port = map['port']
            if port != _NONE:
                settings[port] = device
        self._set_port_options(False)

    def _load_preset_options(self, redraw: bool = True) -> None:
        '''load and set values to options and values to input blocks on preset sub-page; called by self.process_user_input and self._load'''
        if self.preset_new_preset:
            self.preset_preset_name = _ADD_NEW_LABEL
            n = 0
        else:
            _router = ui.router
            output_devices = _router.output_devices_tuple_all
            preset_device_name = '' if len(output_devices) == 0 else output_devices[self.preset_device]
            self.preset_device_name = preset_device_name
            presets_tuples = _router.output_presets_tuples
            if preset_device_name in presets_tuples:
                preset_preset = self.preset_preset
                presets_tuple = () if preset_device_name == '' else presets_tuples[preset_device_name]
                if preset_preset < len(presets_tuple):
                    preset_preset_name = presets_tuple[preset_preset]
                    self.preset_preset_name = preset_preset_name
                    maps = ui.data.output_presets[preset_device_name][preset_preset_name]['maps']
                    n = len(maps)
                else:
                    self.preset_preset_name = _ADD_NEW_LABEL
                    n = 0
            else:
                self.preset_preset_name = _ADD_NEW_LABEL
                n = 0
        preset_maps = self.preset_maps
        for i in range(_MAX_PRESETS):
            preset_maps[i][0] = maps[i][0] if i < n else ''    # trigger
            preset_maps[i][1] = maps[i][1] if i < n else _NONE # note
        self._set_preset_options(redraw)

    def _set_port_options(self, redraw: bool = True) -> None:
        '''set options and values to input blocks on ports sub-page; called by self.process_user_input and self._load_port_options'''
        if self.sub_page != _SUB_PAGE_PORTS:
            return
        devices_tuple = ChainMapTuple(('____',), ui.router.output_devices_tuple_assigned)
        blocks = self.blocks
        selected_port = self.selected_port
        self.selected_port = _NONE
        for port, device in enumerate(self.port_settings):
            if port == _NR_OUT_PORTS:
                break
            if port == selected_port:
                device = self.selected_port_device
            device_option = 0 if device == '' else devices_tuple.index(device)
            blocks[_PORT_FIRST_DEVICE + port].set_options(devices_tuple, device_option, redraw)

    def _set_device_options(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks on device sub-page; called by self.process_user_input, self._load and
        self._callback_confirm'''
        if self.sub_page != _SUB_PAGE_DEVICES:
            return
        devices_tuple = ChainMapTuple(ui.router.output_devices_tuple_all, (_ADD_NEW_LABEL,))
        if len(devices_tuple) == 1:
            self.device_new_device = True
        if self.device_new_device:
            self.device_device_name = _ADD_NEW_LABEL
            channel = 0
            vel_0_note_off = True
            running_status = True
        else:
            device_device_name = str(devices_tuple[self.device_device])
            self.device_device_name = device_device_name
            settings = ui.data.output_devices[device_device_name]
            channel = settings['channel'] + 1 # _NONE becomes 0
            vel_0_note_off = int(settings['vel_0_note_off'])
            running_status = int(settings['running_status'])
        blocks = self.blocks
        blocks[_DEVICE_DEVICE].set_options(devices_tuple, self.device_device, redraw)
        blocks[_DEVICE_CHANNEL].set_options(selection=channel, redraw=redraw)
        blocks[_DEVICE_0_NOTE_OFF].set_options(selection=vel_0_note_off, redraw=redraw)
        blocks[_DEVICE_RUNNING_STATUS].set_options(selection=running_status, redraw=redraw)

    def _set_trigger_options(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks on triggers sub-page; called by self.process_user_input and self._load'''
        if self.sub_page != _SUB_PAGE_TRIGGERS:
            return
        _router = ui.router
        devices_tuple = _router.output_devices_tuple_all
        trigger_device = self.trigger_device
        trigger_device_name = '' if len(devices_tuple) == 0 else str(devices_tuple[trigger_device])
        self.trigger_device_name = trigger_device_name
        if trigger_device_name not in _router.output_triggers_tuples:
            self.trigger_trigger = 0
            triggers_tuple = (_ADD_NEW_LABEL,)
            trigger_trigger_name = _ADD_NEW_LABEL
        else:
            triggers_tuple = ChainMapTuple(_router.output_triggers_tuples[trigger_device_name], (_ADD_NEW_LABEL,))
            trigger_trigger_name = str(triggers_tuple[self.trigger_trigger])
        self.trigger_trigger_name = trigger_trigger_name
        if trigger_trigger_name == _ADD_NEW_LABEL:
            channel = 0
            note = 0
            note_off = 0
            threshold = 0
            curve = 3
            min_velocity = 0
            max_velocity = 127
        else:
            mapping = ui.data.output_devices[trigger_device_name]['mapping'][trigger_trigger_name]
            channel = mapping['channel'] + 1 # _NONE becomes 0
            note = mapping['note'] + 1 # _NONE becomes 0
            note_off = mapping['note_off'] + 1 # _NOTE_OFF_OFF becomes 0
            threshold = mapping['threshold']
            curve = mapping['curve'] + 3 # -3 becomes 0
            min_velocity = mapping['min_velocity']
            max_velocity = mapping['max_velocity']
        blocks = self.blocks
        blocks[_TRIGGER_DEVICE].set_options(devices_tuple, trigger_device, redraw)
        blocks[_TRIGGER_TRIGGER].set_options(triggers_tuple, self.trigger_trigger, redraw)
        blocks[_TRIGGER_CHANNEL].set_options(selection=channel, redraw=redraw)
        blocks[_TRIGGER_NOTE].set_options(selection=note, redraw=redraw)
        blocks[_TRIGGER_NOTE_OFF].set_options(selection=note_off, redraw=redraw)
        blocks[_TRIGGER_THRESHOLD].set_options(selection=threshold, redraw=redraw)
        blocks[_TRIGGER_CURVE].set_options(selection=curve, redraw=redraw)
        blocks[_TRIGGER_MIN_VELOCITY].set_options(selection=min_velocity, redraw=redraw)
        blocks[_TRIGGER_MAX_VELOCITY].set_options(selection=max_velocity, redraw=redraw)

    def _set_preset_options(self, redraw: bool = True) -> None:
        '''set options and values to input blocks on preset sub-page; called by self.process_user_input, self._load_preset_option and self._callback_confirm'''
        if self.sub_page != _SUB_PAGE_PRESETS:
            return
        _router = ui.router
        preset_device_name = self.preset_device_name
        presets_tuples = _router.output_presets_tuples
        if preset_device_name not in presets_tuples:
            self.preset_preset = 0
            presets_tuple = (_ADD_NEW_LABEL,)
        else:
            presets_tuple = ChainMapTuple(presets_tuples[preset_device_name], (_ADD_NEW_LABEL,))
        blocks = self.blocks
        blocks[_PRESET_DEVICE].set_options(_router.output_devices_tuple_all, self.preset_device, redraw)
        blocks[_PRESET_PRESET].set_options(presets_tuple, self.preset_preset, redraw)
        triggers = () if preset_device_name == '' else _router.output_triggers_tuples[preset_device_name]
        triggers_tuple = ChainMapTuple(('____',), triggers)
        clear = self.preset_preset_name == _ADD_NEW_LABEL
        preset_maps = self.preset_maps
        for i in range(_MAX_PRESETS):
            if clear:
                preset_maps[i] = ['', _NONE]
            trigger_option = 0 if preset_maps[i][0] == '' else triggers_tuple.index(preset_maps[i][0])
            blocks[_PRESET_FIRST_MAP + 2 * i].set_options(triggers_tuple, trigger_option, redraw)
            note_option = 0 if preset_maps[i][0] == '' else preset_maps[i][1] + 1 # _NONE becomes 0
            blocks[_PRESET_FIRST_NOTE + 2 * i].set_options(_NOTE_OPTIONS, note_option, redraw)

    def _save_port_settings(self) -> None:
        '''save values from input blocks on ports sub-page; called by self.process_user_input'''
        _data = ui.data
        mapping = _data.output_device_mapping
        selected_port = self.selected_port
        assigned_devices = []
        for device, definition in mapping.items():
            if definition['port'] != _NONE:
                assigned_devices.append(device)
        changed = False
        for port, device in enumerate(self.port_settings):
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
                mapping[device] = {'port': port}
                changed = True
        for device in assigned_devices:
            mapping[device]['port'] = _NONE
            changed = True
        if selected_port_device != '' and mapping[selected_port_device]['port'] == _NONE:
            mapping[selected_port_device] = {'port': selected_port}
            changed = True
        self.selected_port_device = selected_port_device
        if not changed:
            return
        _data.save_data_json_file()
        ui.router.update(False, False, False, False, False, False)

    def _save_device_settings(self, id: int, value: int) -> bool:
        '''save values from input blocks on device sub-page; called by self.process_user_input'''
        _data = ui.data
        changed = False
        device_key = self.device_device_name
        devices = _data.output_devices
        if not device_key in devices:
            devices[device_key] = {'channel': _NONE, 'vel_0_note_off': True, 'running_status': True,'mapping': {}}
            changed = True
        device = devices[device_key]
        if id == _DEVICE_CHANNEL:
            key = 'channel'
            store_value = value - 1 # 0 becomes _NONE
        elif id == _DEVICE_0_NOTE_OFF:
            key = 'vel_0_note_off'
            store_value = bool(value)
        elif id == _DEVICE_RUNNING_STATUS:
            key = 'running_status'
            store_value = bool(value)
        if device[key] != store_value:
            device[key] = store_value
            changed = True
        if changed:
            _data.save_data_json_file()
            ui.router.update(False, False, False, False, False, False)
        return changed

    def _save_trigger_settings(self, id: int, value: int) -> bool:
        '''save values from input blocks on triggers sub-page; called by self.process_user_input'''
        _data = ui.data
        changed = False
        device = _data.output_devices[self.trigger_device_name]
        trigger_key = self.trigger_trigger_name
        mapping = device['mapping']
        if not trigger_key in mapping:
            mapping[trigger_key] = {'channel': _NONE, 'note': _NONE, 'note_off': _NOTE_OFF_OFF}
            changed = True
        trigger = mapping[trigger_key]
        if id == _TRIGGER_CHANNEL:
            key = 'channel'
            store_value = value - 1 # 0 becomes _NONE
        elif id == _TRIGGER_NOTE:
            key = 'note'
            store_value = value - 1 # 0 becomes _NONE
        elif id == _TRIGGER_NOTE_OFF:
            key = 'note_off'
            store_value = value - 1 # 0 becomes _NOTE_OFF_OFF
        elif id == _TRIGGER_THRESHOLD:
            key = 'threshold'
            store_value = value
        elif id == _TRIGGER_CURVE:
            key = 'curve'
            store_value = value - 3 # 0 becomes -3
        elif id == _TRIGGER_MIN_VELOCITY:
            key = 'min_velocity'
            store_value = value
        else: # id == _TRIGGER_MAX_VELOCITY
            key = 'max_velocity'
            store_value = value
        if trigger[key] != store_value:
            trigger[key] = store_value
            changed = True
        if changed:
            _data.save_data_json_file()
            ui.router.update(False, False, False, False, False, False)
        return changed

    def _save_preset_settings(self, id: int, value: int, text: str) -> bool:
        '''save values from input blocks on device sub-page; called by self.process_user_input'''
        _data = ui.data
        changed = False
        device_key = self.preset_device_name
        preset_key = self.preset_preset_name
        presets = _data.output_presets
        if not device_key in presets:
            presets[device_key] = {}
            changed = True
        if not preset_key in presets[device_key]:
            presets[device_key][preset_key] = {'maps': []}
            changed = True
        device_maps = presets[device_key][preset_key]['maps']
        preset_maps = self.preset_maps
        row = (id - _PRESET_FIRST_MAP) // 2
        col = (id - _PRESET_FIRST_MAP) % 2
        if col == 0: # trigger
            store_value = '' if value == 0 else text
        else:        # note
            store_value = value - 1 # 0 becomes _NONE
        preset_maps[row][col] = store_value
        maps = []
        for map in preset_maps:
            if map[0] != '':
                found = False
                for item in maps:
                    if map[0] == item[0]:
                        item[1] = map[1]
                        found = True
                        break
                if not found:
                    maps.append(map)
        if len(maps) != len(device_maps):
            changed = True
        else:
            for i, map in enumerate(device_maps):
                if map[0] != maps[i]:
                    changed = True
                    break
        if changed:
            for i in range(min(len(device_maps), len(maps))):
                if device_maps[i] != maps[i]:
                    device_maps[i][0] = maps[i][0]
                    device_maps[i][1] = maps[i][1]
            while len(device_maps) > len(maps):
                del device_maps[-1]
            while len(maps) > len(device_maps):
                device_maps.append(maps[len(device_maps)])
            _data.save_data_json_file()
            ui.router.update(False, False, False, False, False, False)
        return changed

    def _callback_text_edit(self, caller_id: int, text: str) -> None:
        '''callback function for text edit pop-up; called (passed on) by self.process_user_input'''
        if text == '':
            return
        sub_page = self.sub_page
        if sub_page == _SUB_PAGE_DEVICES and caller_id == _DEVICE_DEVICE:
            if self.device_device_name == text:
                return
            if self.device_new_device:
                self.device_new_device = False
                ui.router.add_device(text, False)
            else:
                ui.router.rename_device(self.device_device_name, text, False)
        elif sub_page == _SUB_PAGE_TRIGGERS and caller_id == _TRIGGER_TRIGGER:
            if self.trigger_trigger_name == text:
                return
            if self.trigger_trigger_name == _ADD_NEW_LABEL:
                self.trigger_new_trigger = False
                ui.router.add_trigger(self.trigger_device_name, text, False)
            else:
                ui.router.rename_trigger(self.trigger_device_name, self.trigger_trigger_name, text, False)
        elif sub_page == _SUB_PAGE_PRESETS and caller_id == _PRESET_PRESET:
            if self.preset_preset_name == text:
                return
            if self.preset_preset_name == _ADD_NEW_LABEL:
                self.preset_new_preset = False
                ui.router.add_preset(self.preset_device_name, text, False)
            else:
                ui.router.rename_preset(self.preset_device_name, self.preset_preset_name, text, False)

    def _callback_confirm(self, caller_id: int, confirm: bool) -> None:
        '''callback for confirm pop-up; called (passed on) by self.process_user_input'''
        if not confirm:
            return
        if caller_id == _DEVICE_DEVICE:
            ui.router.delete_device(self.device_device_name, True)
            if self.device_device > 0:
                self.device_device -= 1
            self._set_device_options()
        elif caller_id == _TRIGGER_TRIGGER:
            ui.router.delete_trigger(self.trigger_device_name, self. trigger_trigger_name, True)
            if self.trigger_trigger > 0:
                self.trigger_trigger -= 1
            self._set_device_options()
        elif id == _PRESET_PRESET:
            ui.router.delete_preset(self.preset_device_name, self.preset_preset_name, True)
            if self.preset_preset > 0:
                self.preset_preset -= 1
            self._set_preset_options()