''' Library providing input pages class for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024-2025 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

_INITIAL_SUB_PAGE = const(0)

import main_loops as ml
from data_types import GenOptions
from ui_pages import Page
from ui_blocks import TitleBar, SelectBlock, TextBlock, TextRow
from constants import CHANNEL_OPTIONS, NOTE_OPTIONS, CC_OPTIONS, CC_VALUE_OPTIONS, TRIGGERS, TRIGGERS_SHORT, TRIGGERS_LONG, TEXT_ROWS_INPUT

_NONE               = const(-1)

_NR_IN_PORTS        = const(6)
_MAX_ZONES          = const(4)

_TEXT_ROW_Y         = const(163)
_TEXT_ROW_H         = const(13)

_BACK_COLOR         = const(0xAA29) # 0x29AA dark purple blue
_FORE_COLOR         = const(0xD9CD) # 0xCDD9 light purple grey

_ALIGN_CENTRE       = const(1)

_ENCODER_NAV        = const(0)

_SUB_PAGES          = const(2)
_SUB_PAGE_PORTS     = const(0)
_SUB_PAGE_NOTES     = const(1)

_SELECT_SUB_PAGE    = const(-1)
_PORT_FIRST_DEVICE  = const(0)
_PORT_FIRST_CHANNEL = const(1)
_NOTE_INPUT_TRIGGER = const(0)
_NOTE_DEVICE        = const(1)
_NOTE_FIRST_NOTE    = const(2)
_NOTE_FIRST_CC      = const(3)
_NOTE_FIRST_CC_MIN  = const(4)
_NOTE_FIRST_CC_MAX  = const(5)

_POP_UP_TEXT_EDIT   = const(0)
_POP_UP_CONFIRM     = const(3)

class PageInput(Page):
    '''input page class; initiated once by ui.__init__'''

    def __init__(self, id: int, x: int, y: int, w: int, h: int, visible: bool) -> None:
        super().__init__(id, x, y, w, h, _SUB_PAGES, visible)
        self.sub_page = _INITIAL_SUB_PAGE
        self.port_settings = [['', _NONE] for _ in range(_NR_IN_PORTS)]
        self.selected_port = 0
        self.map_settings = [[_NONE, _NONE, 0 , 127] for _ in range(_MAX_ZONES)]
        self.device_options = GenOptions(_NR_IN_PORTS, func=self._device_options)
        self.page_is_built = False
        self._build_page()

    def program_change(self, update_only: bool) -> None:
        '''update page after program change; called by ui.program_change'''
        if self.visible:
            self._load()
        else:
            blocks = self.blocks
            if (selected_block := self.selected_block[self.sub_page]) != 0:
                blocks[selected_block].update(False, False)
                blocks[0].update(True, False)

    def encoder(self, encoder_id: int, value: int, page_select_mode: bool) -> bool:
        '''process encoder input at page level (ui.process_encoder > Page.encoder/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by ui.process_encoder_input'''
        if super().encoder(encoder_id, value, page_select_mode):
            self._set_text_row()
            if encoder_id != _ENCODER_NAV:
                return True
            if self.sub_page == _SUB_PAGE_PORTS:
                self.selected_port = (value - _PORT_FIRST_DEVICE) // 2
            elif value >= _NOTE_FIRST_NOTE: # sub_page == _SUB_PAGE_NOTE
                ml.router.set_trigger(zone=(value - _NOTE_FIRST_NOTE) // 4)
            return True
        return False

    def process_user_input(self, id: int, value: int|str = _NONE, button_del: bool = False, button_sel_opt: bool = False) -> bool:
        '''process user input at page level (ui.set_user_input_tuple > ui.user_input_tuple > ui.process_user_input >
        Page/PagesTab.process_user_input); called by ui.process_user_input'''
        if type(value) is str:
            value_str = value
            value = _NONE
            value_is_none = False
        else:
            value = int(value)
            value_is_none = value == _NONE
        if id == _SELECT_SUB_PAGE:
            if button_del or button_sel_opt or value_is_none or value == self.sub_page:
                return False
            self._set_sub_page(value)
            self._load()
            return True
        if self.sub_page == _SUB_PAGE_PORTS:
            if button_del:
                ml.ui.pop_ups[_POP_UP_CONFIRM].open(self, id, 'clear name?', self._callback_confirm)
                return True
            elif button_sel_opt:
                if (id - _PORT_FIRST_DEVICE) % 2 == 0: # name
                    text = self.port_settings[(id - _PORT_FIRST_DEVICE) // 2][0]
                    ml.ui.pop_ups[_POP_UP_TEXT_EDIT].open(self, id, text, callback_func=self.callback_input)
                return True
            elif value_is_none:
                return False
            row, col = divmod(id - _PORT_FIRST_DEVICE, 2)
            if col == 0: # name
                self.port_settings[row][col] = value_str
            else:        # channel
                self.port_settings[row][col] = _NONE if value == _NONE else value - 1 # value == 0 becomes _NONE
            if self._save_port_settings():
                self._set_port_options()
        else: # sub_page == _SUB_PAGE_NOTES
            if button_del or button_sel_opt or value_is_none:
                return False
            elif id == _NOTE_INPUT_TRIGGER:
                ml.ui.set_trigger(value)
            elif id == _NOTE_DEVICE:
                self.selected_port = value
                if self._save_map_settings():
                    self._set_map_options()
            else:
                row, col = divmod(id - _NOTE_FIRST_NOTE, 4)
                if col <= 1:
                    value -= 1 # 0 becomes _NONE
                self.map_settings[row][col] = value
                if self._save_map_settings():
                    self._set_map_options()
        return True

    def set_trigger(self) -> None:
        '''set active trigger (triggered by trigger button) at page level; called by ui.set_trigger (also calling router.set_trigger)'''
        if self.sub_page != _SUB_PAGE_PORTS:
            self._load()

###### TO BE DOCUMENTED: MIDI LEARN ALSO WORKS ON SELECTED PORT FOR INPUT PAGE, NOT ON MIDI LEARN PORT
    def midi_learn(self, port: int, channel: int, trigger: int, zone: int, note: int, program: int, cc: int, cc_value: int) -> bool:
        '''process midi learn input, save settings and reload options; called by ui.process_midi_learn_data'''
        block = self.selected_block[(sub_page := self.sub_page)]
        if sub_page == _SUB_PAGE_PORTS:
            if channel == _NONE:
                return False
            row, col = divmod(block - _PORT_FIRST_DEVICE, 2)
            if col == 0 or row != port: # device or different input device
                return False
            value = channel + 1 # _NONE becomes 0
        else: # sub_page == _SUB_PAGE_NOTES
            if block == _NOTE_INPUT_TRIGGER:
                if trigger == _NONE:
                    return False
                triggers_short = TRIGGERS_SHORT
                trigger_short = triggers_short[trigger]
                zone_name = TRIGGERS[trigger][2][0][zone]
                self.blocks[_NOTE_INPUT_TRIGGER].set_value(f'{trigger_short}{zone_name}', False)
                ml.ui.set_trigger(trigger, zone)
                return True
            elif block == _NOTE_DEVICE:
                if port == _NONE:
                    return False
                value = port
            else:
                row, col = divmod(block - _NOTE_FIRST_NOTE, 4)
                if row != self.selected_port: # different input device
                    return False
                if col == 0:
                    value = note + 1 # _NONE becomes 0
                elif col == 1:
                    value = cc + 1 # _NONE becomes 0
                else:
                    value = cc_value
                if value == _NONE:
                    return False
        return self.blocks[block].set_selection(value)

    def _build_page(self) -> None:
        '''build page (without drawing it); called by self.__init__ and self._build_sub_page'''
        if self.page_is_built:
            return
        self.page_is_built = True
        _build_sub_page = self._build_sub_page
        sub_pages_title_bars = self.sub_pages_title_bars
        sub_pages_blocks = self.sub_pages_blocks
        sub_pages_empty_blocks = self.sub_pages_empty_blocks
        sub_pages_text_rows = self.sub_pages_text_rows
        for i in range(_SUB_PAGES):
            title_bar, blocks, empty_blocks, text_row = _build_sub_page(i)
            sub_pages_title_bars.append(title_bar)
            sub_pages_blocks.append(blocks)
            sub_pages_empty_blocks.append(empty_blocks)
            sub_pages_text_rows.append(text_row)
        self._set_sub_page(self.sub_page)

    def _build_sub_page(self, sub_page: int) -> tuple:
        '''build sub-page (without drawing it); called by self._build_page'''
        if not self.page_is_built:
            self._build_page()
            return None, [], []
        blocks = []
        empty_blocks = []
        selected_block = self.selected_block[sub_page]
        _callback_input = self.callback_input
        if sub_page == _SUB_PAGE_PORTS:
            title_bar = TitleBar('input ports', 1, _SUB_PAGES)
            row = -1
            for i in range(_NR_IN_PORTS):
                row += 1
                blocks.append(TextBlock(_PORT_FIRST_DEVICE + 2 * i, row, 0, 3, 4, selected_block == _PORT_FIRST_DEVICE + 2 * i,
                                          f'p{i + 1}: device name', callback_func=_callback_input))
                blocks.append(SelectBlock(_PORT_FIRST_CHANNEL + 2 * i, row, 3, 1, 4, selected_block == _PORT_FIRST_CHANNEL + 2 * i,
                                          'channel', CHANNEL_OPTIONS, default_selection=0, callback_func=_callback_input))
        else: # sub_page == _SUB_PAGE_NOTES
            title_bar = TitleBar('input notes/pedal cc', 2, _SUB_PAGES)
            blocks.append(SelectBlock(_NOTE_INPUT_TRIGGER, 0, 0, 1, 1, selected_block == _NOTE_INPUT_TRIGGER, 'input trigger',
                                      TRIGGERS_LONG, add_line=True, callback_func=_callback_input))
            blocks.append(SelectBlock(_NOTE_DEVICE, 1, 0, 1, 1, selected_block == _NOTE_DEVICE, 'port/device',
                                      callback_func=_callback_input))
            for i in range(_MAX_ZONES):
                blocks.append(SelectBlock(_NOTE_FIRST_NOTE + i, i + 2, 0, 1, 4, selected_block == _NOTE_FIRST_NOTE + i,
                                          callback_func=_callback_input))
                blocks.append(SelectBlock(_NOTE_FIRST_CC + i, i + 2, 1, 1, 4, selected_block == _NOTE_FIRST_CC + i, default_selection=0,
                                          callback_func=_callback_input))
                blocks.append(SelectBlock(_NOTE_FIRST_CC_MIN + i, i + 2, 2, 1, 4, selected_block == _NOTE_FIRST_CC_MIN + i,
                                          default_selection=0, callback_func=_callback_input))
                blocks.append(SelectBlock(_NOTE_FIRST_CC_MAX + i, i + 2, 3, 1, 4, selected_block == _NOTE_FIRST_CC_MAX + i,
                                          default_selection=127, callback_func=_callback_input))
        text_row = TextRow(_TEXT_ROW_Y, _TEXT_ROW_H, _BACK_COLOR, _FORE_COLOR, _ALIGN_CENTRE)
        return title_bar, blocks, empty_blocks, text_row

    def _load(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks; called by self.set_visibility, Page*.program_change and Page*.process_user_input'''
        redraw &= ml.ui.active_pop_up is None
        self._load_port_options()
        self._load_map_options(False)
        if redraw:
            self._set_text_row(False)
            self.draw()

    def _set_text_row(self, redraw: bool = True) -> None:
        '''draw text row with long description of currently selected block; called by self.encoder and self._load'''
        selection = self.selected_block[(sub_page := self.sub_page)]
        if sub_page == _SUB_PAGE_PORTS:
            text = TEXT_ROWS_INPUT[_SUB_PAGE_PORTS][selection]
        else: # sub_page == _SUB_PAGE_NOTES
            if selection == _NOTE_INPUT_TRIGGER:
                text = TEXT_ROWS_INPUT[_SUB_PAGE_NOTES][_NOTE_INPUT_TRIGGER]
            elif selection == _NOTE_DEVICE:
                text = TEXT_ROWS_INPUT[_SUB_PAGE_NOTES][_NOTE_DEVICE] + TRIGGERS_SHORT[ml.router.input_trigger]
            else:
                row, col = divmod(selection - _NOTE_FIRST_NOTE, 4)
                _router = ml.router
                trigger_short = TRIGGERS_SHORT[_router.input_trigger]
                if row < len(zone_names := TRIGGERS[_router.input_trigger][2][1]):
                    if col == 0:
                        text = f'input note for {trigger_short} {zone_names[row]}'
                    elif col == 1:
                        text = f'pedal cc number for {trigger_short} {zone_names[row]}'
                    elif col == 2:
                        text = f'min pedal cc value for {trigger_short} {zone_names[row]}'
                    else:
                        text = f'max pedal cc value for {trigger_short} {zone_names[row]}'
                else:
                    text = ''
        self.text_row.set_text(text, redraw) # type: ignore

    def _load_port_options(self) -> None:
        '''load and set values to input blocks on ports sub-page; called by self._load'''
        settings = self.port_settings
        for port, (name, channel) in enumerate(ml.data.input_port_mapping):
            map = settings[port]
            map[0] = name
            map[1] = channel
        self._set_port_options()

    def _load_map_options(self, redraw: bool = True) -> None:
        '''load and set values to options and values to input blocks on mapping sub-pages; called by self.set_trigger and self._load'''
        settings = self.map_settings
        _ml = ml
        if len(input_triggers := _ml.data.input_triggers) == 0:
            zones_count = 0
        else:
            triggers = input_triggers[(trigger_short := TRIGGERS_SHORT[_ml.router.input_trigger])]
            self.selected_port = triggers['port']
            zones_count = len(TRIGGERS[TRIGGERS_SHORT.index(trigger_short)][2][0])
            for zone, trigger_map in enumerate(triggers['mapping']):
                map = settings[zone]
                if (cc_min := trigger_map['cc_min']) == -1:
                    cc_min = 0
                if (cc_max := trigger_map['cc_max']) == -1:
                    cc_max = 127
                map[0] = trigger_map['note']
                map[1] = trigger_map['pedal_cc']
                map[2] = cc_min
                map[3] = cc_max
        if (n := _MAX_ZONES - zones_count) > 0:
            for i in range(n):
                settings[(m := zones_count + i)][0] = _NONE
                settings[m][1] = _NONE
                settings[m][2] = 0
                settings[m][3] = 127
        self._set_map_options(redraw)

    def _set_port_options(self) -> None:
        '''set options and values to input blocks on ports sub-page; called by self._load_port_options'''
        if self.sub_page != _SUB_PAGE_PORTS:
            return
        blocks = self.blocks
        for port, (name, channel) in enumerate(self.port_settings):
            if name == '':
                name = f'[port {port + 1}]'
            blocks[_PORT_FIRST_DEVICE + 2 * port].set_value(name, False)
            channel += 1 # _NONE becomes 0
            blocks[_PORT_FIRST_CHANNEL + 2 * port].set_options(selection=channel, redraw=False)

    def _set_map_options(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks on mapping sub-pages; called by self.process_user_input and
        self._load_map_options'''
        if self.sub_page != _SUB_PAGE_NOTES:
            return
        _router = ml.router
        blocks = self.blocks
        blocks[_NOTE_INPUT_TRIGGER].set_options(selection=_router.input_trigger, redraw=False)
        blocks[_NOTE_DEVICE].set_options(self.device_options, self.selected_port, 0, redraw)
        zones_count = len(zone_icons := TRIGGERS[_router.input_trigger][2][0])
        for row, (note, cc, cc_min, cc_max) in enumerate(self.map_settings):
            block = blocks[_NOTE_FIRST_NOTE + 4 * row]
            if row < zones_count:
                block.enable(True, redraw=False)
                if (icon := zone_icons[row]) != '':
                    icon += ' '
                note += 1 # _NONE becomes 0
                block.set_label(f'{icon}note', False)
                block.set_options(NOTE_OPTIONS, note, 0, redraw)
            else:
                block.enable(False, False, redraw=redraw)
            block = blocks[_NOTE_FIRST_CC + 4 * row]
            if row < zones_count:
                block.enable(True, redraw=False)
                cc += 1 # _NONE becomes 0
                block.set_label('pedal cc', False)
                block.set_options(CC_OPTIONS, cc, 0, redraw)
            else:
                block.enable(False, False, redraw=redraw)
            block = blocks[_NOTE_FIRST_CC_MIN + 4 * row]
            if row < zones_count:
                if cc == 0:
                    block.enable(False, redraw=False)
                    block.set_label('', False)
                    block.set_options(redraw=redraw)
                else:
                    block.enable(True, redraw=False)
                    block.set_label('cc min', False)
                    block.set_options(CC_VALUE_OPTIONS, cc_min, 0, redraw)
            else:
                block.enable(False, False, redraw=redraw)
            block = blocks[_NOTE_FIRST_CC_MAX + 4 * row]
            if row < zones_count:
                if cc == 0:
                    block.enable(False, redraw=False)
                    block.set_label('', False)
                    block.set_options(redraw=redraw)
                else:
                    block.enable(True, redraw=redraw)
                    block.set_label('cc max', False)
                    block.set_options(CC_VALUE_OPTIONS, cc_max, 127, redraw)
            else:
                block.enable(False, False, redraw=redraw)

    def _save_port_settings(self) -> bool:
        '''save values from input blocks on ports sub-page; called by self.process_user_input'''
        _ml = ml
        _data = _ml.data
        _router = _ml.router
        _router.handshake() # request second thread to wait
        mapping = _data.input_port_mapping
        settings = self.port_settings
        selected_device = settings[(selected_port := self.selected_port)][0]
        if selected_device != '':
            for port, (name, _) in enumerate(settings):
                if port == selected_port:
                    continue
                if name == selected_device:
                    settings[port][0] = ''
        changed = False
        for port, (name, channel) in enumerate(settings):
            map = mapping[port]
            if map[0] != name:
                map[0] = name
                changed = True
            if map[1] != channel:
                map[1] = channel
                changed = True
        if changed:
            _data.save_data_json_file()
            _router.update(already_waiting=True)
        else:
            _router.resume() #resume second thread
        return changed

    def _save_map_settings(self, redraw: bool = True) -> bool:
        '''save values from input blocks on mapping sub-pages; called by self.process_user_input and self.midi_learn'''
        _ml = ml
        _data = _ml.data
        _router = _ml.router
        _router.handshake() # request second thread to wait
        input_triggers = _data.input_triggers
        triggers = input_triggers[TRIGGERS_SHORT[_router.input_trigger]]
        changed = False
        if self.selected_port != triggers['port']:
            triggers['port'] = self.selected_port
            changed = True
        zones_count = len(TRIGGERS[_router.input_trigger][2][0])
        for zone, (note, cc, cc_min, cc_max) in enumerate(self.map_settings):
            if zone < zones_count:
                trigger = triggers['mapping'][zone]
                if trigger['note'] != note:
                    trigger['note'] = note
                    changed = True
                if trigger['pedal_cc'] != cc:
                    trigger['pedal_cc'] = cc
                    changed = True
                if cc == _NONE:
                    cc_min = _NONE
                    cc_max = _NONE
                if trigger['cc_min'] != cc_min:
                    trigger['cc_min'] = cc_min
                    changed = True
                if trigger['cc_max'] != cc_max:
                    trigger['cc_max'] = cc_max
                    changed = True
        if changed:
            _data.save_data_json_file()
            _router.update(already_waiting=True)
        else:
            _router.resume() # resume second thread
        return changed

    def _callback_confirm(self, caller_id: int, confirm: bool) -> None:
        '''callback for confirm pop-up; called (passed on) by self.process_user_input'''
        if not confirm:
            return
        self.port_settings[(caller_id - _PORT_FIRST_DEVICE) // 2][0] = ''
        self._save_port_settings()

    def _device_options(self, i: int) -> str:
        '''function to pass on to device options generator'''
        device = self.port_settings[i][0]
        return f'p{i + 1}' if device == '' else f'p{i + 1}: {device}'