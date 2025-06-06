''' Library providing output pages class for Cybo-Drummer - Humanize Those Drum Computers!
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
from ui_blocks import TitleBar, EmptyRow, CheckBoxBlock, SelectBlock, TextBlock, TextRow
from constants import CONTEXT_MENU_ITEMS, START_OPTION, CHANNEL_OPTIONS, NOTE_OPTIONS, NOTE_OFF_OPTIONS_WO, VELOCITY_OPTIONS, \
    CURVE_OPTIONS, TEXT_ROWS_OUTPUT

_NONE                  = const(-1)

_TEXT_ROW_Y            = const(163)
_TEXT_ROW_H            = const(13)

_BACK_COLOR            = const(0xAA29) # 0x29AA dark purple blue
_FORE_COLOR            = const(0xD9CD) # 0xCDD9 light purple grey

_ALIGN_CENTRE          = const(1)

_NR_OUT_PORTS          = const(6)

_NOTE_OFF_OFF          = const(-1) 

_ADD_NEW_LABEL         = '[add new]'

_MAX_LABEL_LENGTH      = const(33)

_ENCODER_NAV           = const(0)

_SUB_PAGES             = const(3)
_SUB_PAGE_PORTS        = const(0)
_SUB_PAGE_DEVICE       = const(1)
_SUB_PAGE_VOICE        = const(2)

_SELECT_SUB_PAGE       = const(-1)
_PORT_FIRST_DEVICE     = const(0)
_DEVICE_DEVICE         = const(0)
_DEVICE_CHANNEL        = const(1)
_DEVICE_0_NOTE_OFF     = const(2)
_DEVICE_RUNNING_STATUS = const(3)
_VOICE_DEVICE          = const(0)
_VOICE_VOICE           = const(1)
_VOICE_CHANNEL         = const(2)
_VOICE_NOTE            = const(3)
_VOICE_NOTE_OFF        = const(4)
_VOICE_THRESHOLD       = const(5)
_VOICE_CURVE           = const(6)
_VOICE_MIN_VELOCITY    = const(7)
_VOICE_MAX_VELOCITY    = const(8)

_POP_UP_TEXT_EDIT      = const(0)
_POP_UP_SELECT         = const(1)
_POP_UP_MENU           = const(2)
_POP_UP_CONFIRM        = const(3)
_POP_UP_MESSAGE        = const(4)

_RENAME                = const(0)
_MOVE_BACKWARD         = const(1)
_MOVE_FORWARD          = const(2)
# _MOVE_TO               = const(3)

_SELECT_POSITION       = const(0)

class PageOutput(Page):
    '''output page class; initiated once by ui.__init__'''

    def __init__(self, id: int, x: int, y: int, w: int, h: int, visible: bool) -> None:
        super().__init__(id, x, y, w, h, _SUB_PAGES, visible)
        self.sub_page = _INITIAL_SUB_PAGE
        self.port_settings = [''] * _NR_OUT_PORTS
        self.selected_port = 0
        self.voice_voice = 0
        self.voice_name = ''
        self.voice_is_new = False
        self.selected_port_device = ''
        self.device_options = GenOptions(_NR_OUT_PORTS, func=self._device_options)
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
            if encoder_id != _ENCODER_NAV or self.sub_page != _SUB_PAGE_PORTS:
                return True
            if self.sub_page == _SUB_PAGE_PORTS:
                self.selected_port = value - _PORT_FIRST_DEVICE
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
        sub_page = self.sub_page
        if sub_page == _SUB_PAGE_PORTS:
            if button_del:
                ml.ui.pop_ups[_POP_UP_CONFIRM].open(self, id, 'clear name?', self._callback_confirm)
                return True
            elif button_sel_opt:
                text = self.port_settings[id - _PORT_FIRST_DEVICE]
                ml.ui.pop_ups[_POP_UP_TEXT_EDIT].open(self, id, text, callback_func=self.callback_input)
                return True
            elif value_is_none:
                return False
            self.port_settings[id - _PORT_FIRST_DEVICE] = value_str
            self._save_port_settings()
        elif sub_page == _SUB_PAGE_DEVICE:
            if button_del or button_sel_opt:
                return False
            elif value_is_none:
                return False
            elif id == _DEVICE_DEVICE:
                if value == _NONE or value == self.selected_port:
                    return False
                self.selected_port = value
                self._set_device_options()
            else: # device settings
                if value == _NONE:
                    return False
                if self._save_device_settings(id, value):
                    self._set_device_options()
        else: # sub_page == _SUB_PAGE_VOICE
            if button_del:
                if id == _VOICE_VOICE:
                    ml.ui.pop_ups[_POP_UP_CONFIRM].open(self, _VOICE_VOICE, 'delete?', self._callback_confirm)
            elif button_sel_opt:
                if id == _VOICE_VOICE:
                    if self.voice_is_new:
                        ml.ui.pop_ups[_POP_UP_TEXT_EDIT].open(self, _VOICE_VOICE, '', callback_func=self._callback_text_edit)
                    else:
                        ml.ui.pop_ups[_POP_UP_MENU].open(self, CONTEXT_MENU_ITEMS, callback_func=self._callback_menu)
            elif value_is_none:
                return False
            elif id == _VOICE_DEVICE:
                if value == _NONE or value == self.selected_port:
                    return False
                self.selected_port = value
                self.voice_voice = 0
                self.voice_name = self.device_options[0]
                self._set_voice_options()
            elif id == _VOICE_VOICE:
                if value == _NONE or value == self.voice_voice:
                    return False
                self.voice_voice = value
                self.voice_name = (text := self.voices[value])
                self.voice_is_new = text == _ADD_NEW_LABEL
                self._set_voice_options()
            else: # device settings
                if value == _NONE or self.voice_is_new:
                    return False
                if self._save_voice_settings(id, value):
                    self._set_voice_options()
        return True

    def midi_learn(self, port: int, channel: int, trigger: int, zone: int, note: int, program: int, cc: int, cc_value: int) -> bool:
        '''process midi learn input, save settings and reload options; called by ui.process_midi_learn_data'''
        block = self.selected_block[(sub_page := self.sub_page)]
        if sub_page == _SUB_PAGE_DEVICE:
            if block == _DEVICE_CHANNEL:
                if channel == _NONE:
                    return False
                value = channel + 1 # _NONE becomes 0
            else:
                return False
        elif sub_page == _SUB_PAGE_VOICE:
            if block == _VOICE_CHANNEL:
                if channel == _NONE or self.voice_is_new:
                    return False
                value = channel + 1 # _NONE becomes 0
            elif block == _VOICE_NOTE:
                if note == _NONE or self.voice_is_new:
                    return False
                value = note + 1 # _NONE becomes 0
            else:
                return False
        else:
            return False
        return self.blocks[block].set_selection(value)

    def _build_page(self) -> None:
        '''build page (without drawing it); called by self.__init__ and self._build_sub_page'''
        if self.sub_page is None or self.page_is_built:
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
            title_bar = TitleBar('output ports', 1, _SUB_PAGES)
            for i in range(_NR_OUT_PORTS):
                blocks.append(TextBlock(_PORT_FIRST_DEVICE + i, i, 0, 2, 2, selected_block == _PORT_FIRST_DEVICE + i,
                                        f'p{i + 1}: device name', callback_func=_callback_input))
        elif sub_page == _SUB_PAGE_DEVICE:
            title_bar = TitleBar('output device', 2, _SUB_PAGES)
            blocks.append(SelectBlock(_DEVICE_DEVICE, 0, 0, 2, 2, selected_block == _DEVICE_DEVICE, 'port/device', add_line=True,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_DEVICE_CHANNEL, 1, 0, 2, 2, selected_block == _DEVICE_CHANNEL, 'channel', CHANNEL_OPTIONS,
                                      default_selection=0, callback_func=_callback_input))
            blocks.append(CheckBoxBlock(_DEVICE_0_NOTE_OFF, 2, 0, 1, 1, selected_block == _DEVICE_0_NOTE_OFF, '0 velocity as note off',
                                        default_selection=True, callback_func=_callback_input))
            blocks.append(CheckBoxBlock(_DEVICE_RUNNING_STATUS, 3, 0, 1, 1, selected_block == _DEVICE_RUNNING_STATUS, 'running status',
                                        default_selection=True, callback_func=_callback_input))
            empty_blocks.append(EmptyRow(4))
            empty_blocks.append(EmptyRow(5))
        else: # sub_page == _SUB_PAGE_VOICE
            title_bar = TitleBar('output voice', 3, _SUB_PAGES)
            blocks.append(SelectBlock(_VOICE_DEVICE, 0, 0, 1, 1, selected_block == _VOICE_DEVICE, 'port/device',
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_VOICE_VOICE, 1, 0, 1, 1, selected_block == _VOICE_VOICE, 'voice', add_line=True,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_VOICE_CHANNEL, 2, 0, 1, 3, selected_block == _VOICE_CHANNEL, 'channel', CHANNEL_OPTIONS,
                                      default_selection=0, callback_func=_callback_input))
            blocks.append(SelectBlock(_VOICE_NOTE, 2, 1, 1, 3, selected_block == _VOICE_NOTE, 'note', NOTE_OPTIONS,
                                      default_selection=0, callback_func=_callback_input))
            blocks.append(SelectBlock(_VOICE_NOTE_OFF, 2, 2, 1, 3, selected_block == _VOICE_NOTE_OFF, 'note off', NOTE_OFF_OPTIONS_WO,
                                      default_selection=0, callback_func=_callback_input))
            blocks.append(SelectBlock(_VOICE_THRESHOLD, 3, 0, 1, 2, selected_block == _VOICE_THRESHOLD, 'vel threshold', VELOCITY_OPTIONS,
                                      default_selection=0, callback_func=_callback_input))
            blocks.append(SelectBlock(_VOICE_CURVE, 3, 1, 1, 2, selected_block == _VOICE_CURVE, 'velocity curve', CURVE_OPTIONS,
                                      default_selection=3, callback_func=_callback_input))
            blocks.append(SelectBlock(_VOICE_MIN_VELOCITY, 4, 0, 1, 2, selected_block == _VOICE_MIN_VELOCITY, 'min velocity',
                                      VELOCITY_OPTIONS, default_selection=0, callback_func=_callback_input))
            blocks.append(SelectBlock(_VOICE_MAX_VELOCITY, 4, 1, 1, 2, selected_block == _VOICE_MAX_VELOCITY, 'max velocity',
                                      VELOCITY_OPTIONS, default_selection=127, callback_func=_callback_input))
            empty_blocks.append(EmptyRow(5))
        text_row = TextRow(_TEXT_ROW_Y, _TEXT_ROW_H, _BACK_COLOR, _FORE_COLOR, _ALIGN_CENTRE)
        return title_bar, blocks, empty_blocks, text_row

    def _load(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks; called by self.set_visibility, Page*.program_change and
        Page*.process_user_input'''
        _ml = ml
        redraw &= _ml.ui.active_pop_up is None
        mapping = _ml.data.output_mapping[2 * self.selected_port + 1]['mapping']
        self.voice_name = '' if len(mapping) == 0 else mapping[2 * self.voice_voice]
        self._load_port_options()
        self._set_device_options(False)
        self._set_voice_options(False)
        if redraw:
            self._set_text_row(False)
            self.draw()

    def _set_text_row(self, redraw: bool = True) -> None:
        '''draw text row with long description of currently selected block; called by self.encoder and self._load'''
        selection = self.selected_block[(sub_page := self.sub_page)]
        if sub_page == _SUB_PAGE_PORTS:
            text = TEXT_ROWS_OUTPUT[_SUB_PAGE_PORTS][selection]
        elif sub_page == _SUB_PAGE_DEVICE:
            text = TEXT_ROWS_OUTPUT[_SUB_PAGE_DEVICE][selection]
        else: # sub_page == _SUB_PAGE_VOICE
            if selection == _VOICE_VOICE:
                output_mapping = ml.data.output_mapping
                port = self.selected_port
                if (device := output_mapping[2 * port]) == '':
                    device = f'[port {port + 1}]'
                text = f'selected {device[0:_MAX_LABEL_LENGTH - 15]} voice'
            else:
                text = TEXT_ROWS_OUTPUT[_SUB_PAGE_VOICE][selection]
        self.text_row.set_text(text, redraw) # type: ignore

    def _load_port_options(self) -> None:
        '''load and set values to input blocks on ports sub-page; called by self._load'''
        settings = self.port_settings
        output_mapping = ml.data.output_mapping
        for port in range(_NR_OUT_PORTS):
            settings[port] = output_mapping[2 * port]
        self._set_port_options()

    def _set_port_options(self) -> None:
        '''set options and values to input blocks on ports sub-page; called by self._load_port_options'''
        if self.sub_page != _SUB_PAGE_PORTS:
            return
        blocks = self.blocks
        for port, name in enumerate(self.port_settings):
            if name == '':
                name = f'[port {port + 1}]'
            blocks[_PORT_FIRST_DEVICE + port].set_value(name, False)

    def _set_device_options(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks on device sub-page; called by self.process_user_input and self._load'''
        if self.sub_page != _SUB_PAGE_DEVICE:
            return
        settings = ml.data.output_mapping[2* (port := self.selected_port) + 1]
        blocks = self.blocks
        blocks[_DEVICE_DEVICE].set_options(self.device_options, port, 0, redraw)
        blocks[_DEVICE_CHANNEL].set_options(selection=settings['channel'] + 1, redraw=redraw) # _NONE becomes 0
        blocks[_DEVICE_0_NOTE_OFF].set_checked(settings['vel_0_note_off'], redraw=redraw)
        blocks[_DEVICE_RUNNING_STATUS].set_checked(settings['running_status'], redraw=redraw)

    def _set_voice_options(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks on triggers sub-page; called by self.process_user_input and self._load'''
        if self.sub_page != _SUB_PAGE_VOICE:
            return
        output_mapping = ml.data.output_mapping
        voices = GenOptions(len(output_mapping[2 * (port := self.selected_port) + 1]['mapping']) // 2 + 1,
                            additional_options=(_ADD_NEW_LABEL,), func=lambda i: output_mapping[2 * port + 1]['mapping'][2 * i])
        self.voices = voices
        if (voice := self.voice_voice) == len(voices) - 1: # _ADD_NEW_LABEL
            channel = 0
            note = 0
            note_off = 0
            threshold = 0
            curve = 3
            min_velocity = 0
            max_velocity = 127
        else:
            mapping = output_mapping[2 * port + 1]['mapping'][2 * voice + 1]
            channel = mapping['channel'] + 1 # _NONE becomes 0
            note = mapping['note'] + 1 # _NONE becomes 0
            note_off = mapping['note_off'] + 1 # _NOTE_OFF_OFF becomes 0
            threshold = mapping['threshold']
            curve = mapping['curve'] + 3 # -3 becomes 0
            min_velocity = mapping['min_velocity']
            max_velocity = mapping['max_velocity']
        blocks = self.blocks
        blocks[_VOICE_DEVICE].set_options(self.device_options, port, 0, redraw)
        blocks[_VOICE_VOICE].set_options(voices, self.voice_voice, redraw=redraw)
        blocks[_VOICE_CHANNEL].set_options(selection=channel, redraw=redraw)
        blocks[_VOICE_NOTE].set_options(selection=note, redraw=redraw)
        blocks[_VOICE_NOTE_OFF].set_options(selection=note_off, redraw=redraw)
        blocks[_VOICE_THRESHOLD].set_options(selection=threshold, redraw=redraw)
        blocks[_VOICE_CURVE].set_options(selection=curve, redraw=redraw)
        blocks[_VOICE_MIN_VELOCITY].set_options(selection=min_velocity, redraw=redraw)
        blocks[_VOICE_MAX_VELOCITY].set_options(selection=max_velocity, redraw=redraw)

    def _save_port_settings(self) -> None:
        '''save values from input blocks on ports sub-page; called by self.process_user_input'''
        _ml = ml
        _data = _ml.data
        _router = _ml.router
        _router.handshake() # request second thread to wait
        output_mapping = _data.output_mapping
        settings = self.port_settings
        selected_device = settings[(selected_port := self.selected_port)]
        if selected_device != '':
            for port, name in enumerate(settings):
                if port == selected_port:
                    continue
                if name == selected_device:
                    settings[port] = ''
        changed = False
        for port, name in enumerate(settings):
            if output_mapping[(n := 2 * port)] != name:
                output_mapping[n] = name
                changed = True
        if not changed:
            _router.resume() # resume second thread
            return
        _data.save_data_json_file()
        _router.update(already_waiting=True)

    def _save_device_settings(self, id: int, value: int) -> bool:
        '''save values from input blocks on device sub-page; called by self.process_user_input'''
        _ml = ml
        _data = _ml.data
        _router = _ml.router
        _router.handshake() # request second thread to wait
        changed = False
        device = _data.output_mapping[2 * self.selected_port + 1]
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
            _router.update(already_waiting=True)
        else:
            _router.resume() # resume second thread
        return changed

    def _save_voice_settings(self, id: int, value: int) -> bool:
        '''save values from input blocks on triggers sub-page; called by self.process_user_input'''
        _ml = ml
        _data = _ml.data
        _router = _ml.router
        _router.handshake() # request second thread to wait
        changed = False
        device = _data.output_mapping[2 * self.selected_port + 1]
        mapping = device['mapping']
        if not (voice_name := self.voice_name) in mapping:
            mapping.append(voice_name)
            mapping.append({'channel': _NONE, 'note': _NONE, 'note_off': _NOTE_OFF_OFF})
            changed = True
        voice = mapping[mapping.index(voice_name) + 1]
        if id == _VOICE_CHANNEL:
            key = 'channel'
            store_value = value - 1 # 0 becomes _NONE
        elif id == _VOICE_NOTE:
            key = 'note'
            store_value = value - 1 # 0 becomes _NONE
        elif id == _VOICE_NOTE_OFF:
            key = 'note_off'
            store_value = value - 1 # 0 becomes _NOTE_OFF_OFF
        elif id == _VOICE_THRESHOLD:
            key = 'threshold'
            store_value = value
        elif id == _VOICE_CURVE:
            key = 'curve'
            store_value = value - 3 # 0 becomes -3
        elif id == _VOICE_MIN_VELOCITY:
            key = 'min_velocity'
            store_value = value
        else: # id == _VOICE_MAX_VELOCITY
            key = 'max_velocity'
            store_value = value
        if voice[key] != store_value:
            voice[key] = store_value
            changed = True
        if changed:
            _data.save_data_json_file()
            _router.update(already_waiting=True)
        else:
            _router.resume() # resume second thread
        return changed

    def _callback_text_edit(self, caller_id: int, text: str) -> None:
        '''callback function for text edit pop-up; called (passed on) by self.process_user_input and self. _callback_menu'''
        if text == '' or text == _ADD_NEW_LABEL:
            return
        if self.voice_name == text:
            return
        if self.voice_is_new:
            self.voice_is_new = False
            ml.router.add_voice(self.selected_port, text)
        else:
            self.draw()
            _ml = ml
            _ui = _ml.ui
            _pop_up = _ui.pop_ups[_POP_UP_MESSAGE]
            _pop_up.open(self, 'processing...', False)
            _ui.display.draw_screen()
            _ml.router.rename_voice(self.selected_port, self.voice_name, text)
            _pop_up.close()

    def _callback_confirm(self, caller_id: int, confirm: bool) -> None:
        '''callback for confirm pop-up; called (passed on) by self.process_user_input'''
        if not confirm:
            return
        if self.sub_page == _SUB_PAGE_PORTS:
            self.port_settings[(caller_id - _PORT_FIRST_DEVICE) // 2] = ''
            self._save_port_settings()
        elif caller_id == _VOICE_VOICE:
            ml.router.delete_voice((port := self.selected_port), self.voice_name)
            if (voice := self.voice_voice) > 0:
                voice -= 1
                self.voice_voice = voice
                self.voice_name = ml.data.output_mapping[2 * port + 1]['mapping'][2 * voice]
            self._set_device_options()

    def _callback_menu(self, selection: int) -> None:
        '''callback for menu pop-up; called (passed on) by self.process_user_input'''
        if selection == _RENAME:
            ml.ui.pop_ups[_POP_UP_TEXT_EDIT].open(self, _VOICE_VOICE, self.voice_name, callback_func=self._callback_text_edit)
        elif selection == _MOVE_BACKWARD:
            destination = (source := self.voice_voice) - 1
            if destination >= 0:
                self.voice_voice = destination
                ml.router.move_voice(self.selected_port, source, destination)
            else:
                self.draw()
        elif selection == _MOVE_FORWARD:
            destination = (source := self.voice_voice) + 1
            _ml = ml
            if destination < len(_ml.data.output_mapping[2 * (port := self.selected_port) + 1]['mapping']) // 2:
                self.voice_voice = destination - 1
                _ml.router.move_voice(port, source, destination)
            else:
                self.draw()
        else: # selection == _MOVE_TO
            _ml = ml
            output_mapping = _ml.data.output_mapping
            options = GenOptions(len(output_mapping[2 * (port := self.selected_port) + 1]['mapping']) // 2, first_options=START_OPTION,
                                 func=lambda i: output_mapping[2 * port + 1]['mapping'][2 * i])
            self.draw()
            _ml.ui.pop_ups[_POP_UP_SELECT].open(self, _SELECT_POSITION, 'move after:', options, self.voice_voice + 1, self._callback_select)

    def _callback_select(self, caller_id: int, selection: int) -> None:
        '''callback for select pop-up; called (passed on) by self._callback_menu'''
        if caller_id != _SELECT_POSITION:
            return
        source = self.voice_voice
        if selection == source or selection == source + 1:
            self.draw()
        else:
            self.voice_voice = selection - 1 if selection > source else selection
            ml.router.move_voice(self.selected_port, source, selection)

    def _device_options(self, i: int) -> str:
        '''function to pass on to device options generator'''
        output_mapping = ml.data.output_mapping
        return f'p{i + 1}' if output_mapping[2 * i] == '' else f'p{i + 1}: {output_mapping[2 * i]}'