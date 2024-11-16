''' Ui library for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

from machine import Pin, SPI
import time

from data_types import ChainMapTuple

from display import ILI9225, Font
import font

from ui_pages_tabs import PagesTabs
from ui_page_program import PageProgram
from ui_page_input import PageInput
from ui_page_output import PageOutput
from ui_page_monitor import PageMonitor
from ui_page_settings import PageSettings
from ui_blocks import TextEdit, SelectPopUp, MenuPopUp, ConfirmPopUp, AboutPopUp

from rotary import Rotary
from button import Button

import midi_tools as mt

_NONE                        = const(-1)

_DISPLAY_BAUTRATE            = const(100_000_000) # display specs: 50_000_000; max: _OVERCLOCK_FREQ / 2

_SLEEP_TIME_OUT              = const(600_000) # ms

_ENCODER_0_PIN_A_CLK         = const(15)
_ENCODER_0_PIN_B_DT          = const(14)
_ENCODER_1_PIN_A             = const(27)
_ENCODER_1_PIN_B             = const(26)

# (_BUTTON_BACKSPACE, _BUTTON_SELECT, _BUTTON_PAGE_CANCEL, _BUTTON_TRIGGER_CONFIRM)
_BUTTON_PINS                 = (28, 22, 3, 2) # gpio numbers
_BUTTON_BACKSPACE            = const(0) # encoder 0 button
_BUTTON_SELECT               = const(1) # encoder 1 button
_BUTTON_PAGE_CANCEL          = const(2)
# _BUTTON_TRIGGER_CONFIRM      = const(3)

_BUTTON_EVENT_PRESS          = const(0)
_BUTTON_EVENT_LONG_PRESS     = const(1)

_DISPLAY_SPI                 = const(0)
_DISPLAY_PIN_DC              = const(21)
_DISPLAY_PIN_CS              = const(17)
_DISPLAY_PIN_RST             = const(20)
_DISPLAY_PIN_BACKLIGHT       = const(16)
_DISPLAY_W                   = const(220)
_DISPLAY_H                   = const(176)

_FRAME_PAGE_SELECT           = const(0)
_PAGE_PROGRAM                = const(1)
_PAGE_INPUT                  = const(2)
_PAGE_OUTPUT                 = const(3)
_PAGE_MONITOR                = const(4)
_PAGE_SETTINGS               = const(5)

_POP_UP_TEXT_EDIT            = const(0)
_POP_UP_SELECT               = const(1)
_POP_UP_MENU                 = const(2)
_POP_UP_CONFIRM              = const(3)
_POP_UP_ABOUT                = const(4)

_CONFIRM_SAVE                = const(128) # needs to be higher than block ids
_CONFIRM_REPLACE             = const(129)

_SELECT_TRIGGER              = const(0)
_SELECT_PROGRAM              = const(1)

_ADD_NEW_LABEL               = '[add new]'

_MARGIN                      = const(3)
_PAGES_W                     = const(16)

_MAX_CHARACTERS              = const(34)

_TRIGGER_IN                  = const(1) # start with 1 because used to create negative keys (< 0)
# _TRIGGER_OUT                 = const(2)

_MONITOR_MODE_MIDI_IN        = const(0)
_MONITOR_MODE_MIDI_OUT       = const(1)
_MONITOR_PAGE_ROUTING        = const(0)
_MONITOR_PAGE_MIDI_IN        = const(1)
_MONITOR_PAGE_MIDI_OUT       = const(2)

_COMMAND_NOTE_OFF            = const(0x80)
_COMMAND_NOTE_ON             = const(0x90)
_COMMAND_POLYPHONIC_PRESSURE = const(0xA0)
_COMMAND_CC                  = const(0xB0)
_COMMAND_PROGRAM_CHANGE      = const(0xC0)
_COMMAND_CHANNEL_PRESSURE    = const(0xD0)
_COMMAND_PITCH_BEND          = const(0xE0)
_SYS_SYSEX_START             = const(0xF0)
_SYS_QUARTER_FRAME           = const(0xF1)
_SYS_SONG_POSITION           = const(0xF2)
_SYS_SONG_SELECT             = const(0xF3)
_SYS_TUNE_REQUEST            = const(0xF6)
_SYS_SYSEX_END               = const(0xF7)
_SYS_CLOCK                   = const(0xF8)
_SYS_START                   = const(0xFA)
_SYS_CONTINUE                = const(0xFB)
_SYS_STOP                    = const(0xFC)
_SYS_ACTIVE_SENSING          = const(0xFE)
_SYS_SYSTEM_RESET            = const(0xFF)

_TEXT_NOTE_OFF               = b'NoteOff '
_TEXT_NOTE_ON                = b'NoteOn  '
_TEXT_POLYPHONIC_PRESSURE    = b'PolyPres'
_TEXT_CC                     = b'ContCtrl'
_TEXT_PROGRAM_CHANGE         = b'ProgChng'
_TEXT_CHANNEL_PRESSURE       = b'ChanPres'
_TEXT_PITCH_BEND             = b'PtchBend'
_TEXT_QUARTER_FRAME          = b'SC Qrtr Frme'
_TEXT_SONG_POSITION          = b'SC Song Pos '
_TEXT_SONG_SELECT            = b'SC Song Slct'
_TEXT_TUNE_REQUEST           = b'SC Tune Req '
_TEXT_CLOCK                  = b'SR Clock    '
_TEXT_START                  = b'SR Start    '
_TEXT_CONTINUE               = b'SR Continue '
_TEXT_STOP                   = b'SR Stop     '
_TEXT_ACTIVE_SENSING         = b'SR Act Sens '
_TEXT_SYSTEM_RESET           = b'SR Sys Reset'

ui = None
display = None
spi = None
scr = None
encoder_0 = None
encoder_1 = None
data = None
router = None

user_input_dict = None

class UI():
    '''user interface class; initiated once by main_loops.py: init'''

    def __init__(self) -> None:
        global ui, display, encoder_0, encoder_1
        ui = self
        display = _Display(_DISPLAY_SPI, _DISPLAY_PIN_DC, _DISPLAY_PIN_CS, _DISPLAY_PIN_RST, _DISPLAY_PIN_BACKLIGHT)
        encoder_0 = Rotary(_ENCODER_0_PIN_A_CLK, _ENCODER_0_PIN_B_DT)
        encoder_1 = Rotary(_ENCODER_1_PIN_A, _ENCODER_1_PIN_B)
        self.buttons = [Button(pin, True) for pin in _BUTTON_PINS]
        self.buttons[-1].long_press = True # trigger/confirm
        self.buttons[-2].long_press = True # page/cancel
        self.page_select_mode = False
        self.trigger_timer = None
        self.frames = []
        self.pages = []
        self.active_page = _PAGE_PROGRAM
        ###### change for testing or screenshot
        # self.active_page = _PAGE_OUTPUT
        self.frames.append(PagesTabs(_FRAME_PAGE_SELECT, _DISPLAY_W - _PAGES_W, 0, _PAGES_W, _DISPLAY_H))
        x, y, w, h = 0, 0, _DISPLAY_W - _PAGES_W - _MARGIN, _DISPLAY_H
        frame = PageProgram(_PAGE_PROGRAM, x, y, w, h, self.active_page == _PAGE_PROGRAM)
        self.frames.append(frame)
        self.pages.append(frame)
        frame = PageInput(_PAGE_INPUT, x, y, w, h, self.active_page == _PAGE_INPUT)
        self.frames.append(frame)
        self.pages.append(frame)
        frame = PageOutput(_PAGE_OUTPUT, x, y, w, h, self.active_page == _PAGE_OUTPUT)
        self.frames.append(frame)
        self.pages.append(frame)
        frame = PageMonitor(_PAGE_MONITOR, x, y, w, h, self.active_page == _PAGE_MONITOR)
        self.frames.append(frame)
        self.pages.append(frame)
        frame = PageSettings(_PAGE_SETTINGS, x, y, w, h, self.active_page == _PAGE_SETTINGS)
        self.frames.append(frame)
        self.pages.append(frame)
        self.pop_ups = []
        self.pop_ups.append(TextEdit(_POP_UP_TEXT_EDIT))
        self.pop_ups.append(SelectPopUp(_POP_UP_SELECT))
        self.pop_ups.append(MenuPopUp(_POP_UP_MENU))
        self.pop_ups.append(ConfirmPopUp(_POP_UP_CONFIRM))
        self.pop_ups.append(AboutPopUp(_POP_UP_ABOUT))
        self.active_pop_up = None
        self.sleep = False
        self.sleep_time = time.ticks_ms()

    def link_data_and_router(self, data_object, router_object) -> None:
        '''set global data and router variables; called by main_loops.py: init'''
        global data, router
        data = data_object
        router = router_object

    def check_sleep_time_out(self):
        '''check if enough time has passed to put ui to sleep, called by main_loops.py: main'''
        if not self.sleep and time.ticks_diff(time.ticks_ms(), self.sleep_time) > _SLEEP_TIME_OUT:
            self.sleep = True
            scr.set_display(False) # type: ignore

    def program_change(self) -> None:
        '''update ui after program change; called by router.update'''
        for frame in self.frames:
            frame.program_change()

    def set_trigger(self, device: int = _NONE, preset: int = _NONE) -> None:
        '''set active trigger (triggered by the trigger button), call router.set_trigger and page.set_trigger; called by
        self._callback_select, PageProgram.process_user_input and PageInput.process_user_input'''
        router.set_trigger(device, preset) # type: ignore
        for page in self.pages:
            page.set_trigger()

    def process_encoder_input(self) -> None:
        '''process encoder input (ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder); called by
        main_loops.py: main'''
        value_0 = encoder_0.value() # type: ignore
        value_1 = encoder_1.value() # type: ignore
        if value_0 != _NONE or value_1 != _NONE:
            self._wake_up()
        encoder_values = (value_0, value_1)
        for i in range(2):
            if encoder_values[i] == _NONE:
                continue
            if self.active_pop_up is None:
                if i == 1 and self.page_select_mode:
                    self.frames[_FRAME_PAGE_SELECT].set_page(encoder_values[1])
                else:
                    self.frames[self.active_page].encoder(i, encoder_values[i], self.page_select_mode)
            else: # pop-up visible
                self.active_pop_up.encoder(i, encoder_values[i])

    def process_user_input(self) -> None:
        '''process buttons and other user input (ui.ui.set_user_input_dict > global user_input_dict > ui.process_user_input >
        Page/PagesTab.process_user_input); called by main_loops.py: main'''
        global user_input_dict
        if user_input_dict is not None:
            self._wake_up()
            frame_id = user_input_dict['frame_id']
            block_id = user_input_dict['block_id']
            value = user_input_dict['value']
            text = user_input_dict['text']
            button_encoder_0 = user_input_dict['button_encoder_0']
            button_encoder_1 = user_input_dict['button_encoder_1']
            user_input_dict = None
            self.frames[frame_id].process_user_input(block_id, value, text, button_encoder_0, button_encoder_1)
        _router = router
        for button_number, button in enumerate(self.buttons):
            value = button.value()
            if value == _NONE:
                continue
            self._wake_up()
            if button_number == _BUTTON_BACKSPACE:
                if self.active_pop_up is None:
                    self.frames[self.active_page].button_backspace()
                else: # pop-up visible
                    self.active_pop_up.button_backspace()
                continue
            if button_number == _BUTTON_SELECT:
                if self.active_pop_up is None:
                    self.frames[self.active_page].button_select()
                else: # pop-up visible
                    self.active_pop_up.button_select()
                continue
            if button_number == _BUTTON_PAGE_CANCEL:
                if self.active_pop_up is None:
                    if value == _BUTTON_EVENT_PRESS: # short-press of page button
                        page_select_mode = not self.page_select_mode
                        self.page_select_mode = page_select_mode
                        self.frames[self.active_page].set_page_encoders(page_select_mode)
                        self.frames[_FRAME_PAGE_SELECT].set_page_encoders(page_select_mode)
                    elif not self.page_select_mode: # long-press of page button and not in page select mode
                        options = ChainMapTuple(data.programs_tuple, (_ADD_NEW_LABEL,)) # type: ignore
                        self.pop_ups[_POP_UP_SELECT].open(self.frames[self.active_page], _SELECT_PROGRAM, 'program', options,
                                                          _router.active_program_number, self._callback_select) # type: ignore
                elif value == _BUTTON_EVENT_PRESS: # pop-up visible, short-press of page button
                    if self.active_pop_up.button_cancel():
                        self.frames[self.active_page].restore()
                continue
            # if button_number == _BUTTON_TRIGGER_CONFIRM
            if self.active_pop_up is None:
                page_select_mode = self.page_select_mode
                if value == _BUTTON_EVENT_PRESS and not page_select_mode: # short-press of trigger button and not in page select mode
                    _router.trigger() # type: ignore
                elif value == _BUTTON_EVENT_LONG_PRESS and not page_select_mode: # long-press of trigger button and not in page select mode
                    options = []
                    input_devices_tuple_assigned = _router.input_devices_tuple_assigned # type: ignore
                    input_presets_tuples = _router.input_presets_tuples # type: ignore
                    for key_int in _router.preset_triggers: # type: ignore
                        #  (6)        12           12      2
                        # 111111|000000000000|000000000000|00
                        #       |            |            |
                        #       |     p      |     d      |i
                        #       |     r      |     e      |o
                        tmp = -1 * key_int
                        if tmp & 0b11 != _TRIGGER_IN:
                            continue
                        tmp >>= 2
                        input_device_name = input_devices_tuple_assigned[tmp & 0xFFF]
                        input_preset_name = input_presets_tuples[input_device_name][tmp >> 12]
                        options.append(f'{input_device_name}: {input_preset_name}')
                    self.pop_ups[_POP_UP_SELECT].open(self.frames[self.active_page], _SELECT_TRIGGER, 'input preset trigger:', options,
                                                      _router.preset_trigger_option, self._callback_select) # type: ignore
            else: # pop-up visible
                if value == _BUTTON_EVENT_PRESS: # short-press of trigger button
                    if self.active_pop_up.button_confirm():
                        self.frames[self.active_page].restore()

    def process_midi_learn_data(self, midi_learn_data) -> None:
        '''process midi learn data (router.send_to_monitor > router.midi_learn_data > ui.process_midi_learn_data > Page.midi_learn); called by
        main_loops.py: main'''
        port, channel, note, program, cc, cc_value, route_number = midi_learn_data
        self.frames[self.active_page].midi_learn(port, channel, note, program, cc, cc_value, route_number)

    def process_monitor(self) -> None:
        '''process monitor data (router.send_to_monitor > router.monitor_data > ui.process_monitor > PageMonitor.add_to_monitor); called by
        main_loops.py: main'''
        _router = router
        monitor_data = _router.read_monitor_data() # type: ignore
        if monitor_data is None:
            return
        mode, port, channel, command, data_1, data_2, route_number = monitor_data
        text_routing = ''
        text_midi_in = ''
        text_midi_out = ''
        if route_number != _NONE:
            route = _router.routing[route_number] # type: ignore
            input_device = route['input_device']
            if command == _COMMAND_NOTE_ON:
                input_preset = route['input_preset']
                output_device = route['output_device']
                output_preset = route['output_preset']
                input = f'{input_device} {input_preset}'
                output = f'{output_device} {output_preset}'
                text_routing = f'{input} > {output}'
                l = len(text_routing)
                if l > _MAX_CHARACTERS:
                    l_input = len(input)
                    l_output = len(output)
                    d = l - _MAX_CHARACTERS
                    if l_input > l_output:
                        d_out = (d * l_output) // (l - 3)
                        d_in = d - d_out
                    else:
                        d_in = (d * l_input) // (l - 3)
                        d_out = d - d_in
                    if d_in > 0:
                        input_device = input_device[:(len(input_device) - d_in)]
                    if d_out > 0:
                        output_device = output_device[:(len(output_device) - d_out)]
                    text_routing = f'{input_device} {input_preset} > {output_device} {output_preset}'    
            elif command == _COMMAND_CC:
                text_pedal = f' foot pedal {data_2}'
                text_routing = f'{input_device}{text_pedal}'
                l = len(text_routing)
                if l > _MAX_CHARACTERS:
                    input_device = input_device[:(_MAX_CHARACTERS - len(text_pedal))]
                    text_routing = f'{input_device}{text_pedal}'
        if command == _COMMAND_NOTE_OFF:
            data_1_str = '' if data_1 == _NONE else mt.number_to_note(data_1)
            data_2_str = '' if data_2 == _NONE else str(data_2)
            descriptive_str = f'P{port} C{channel:>2} {_TEXT_NOTE_OFF.decode()} {data_1_str:>3} {data_2_str:>3}'
        elif command == _COMMAND_NOTE_ON:
            data_1_str = '' if data_1 == _NONE else mt.number_to_note(data_1)
            data_2_str = '' if data_2 == _NONE else str(data_2)
            descriptive_str = f'P{port} C{channel:>2} {_TEXT_NOTE_ON.decode()} {data_1_str:>3} {data_2_str:>3}'
        elif command == _COMMAND_POLYPHONIC_PRESSURE:
            descriptive_str = f'P{port} C{channel:>2} {_TEXT_POLYPHONIC_PRESSURE.decode()} {data_1:>3} {data_2:>3}'
        elif command == _COMMAND_CC:
            descriptive_str = f'P{port} C{channel:>2} {_TEXT_CC.decode()} {data_1:>3} {data_2:>3}'
        elif command == _COMMAND_PROGRAM_CHANGE:
            descriptive_str = f'P{port} C{channel:>2} {_TEXT_PROGRAM_CHANGE.decode()} {data_1:>3}    '
        elif command == _COMMAND_CHANNEL_PRESSURE:
            descriptive_str = f'P{port} C{channel:>2} {_TEXT_CHANNEL_PRESSURE.decode()} {data_1:>3}    '
        elif command == _COMMAND_PITCH_BEND:
            value = (data_2 << 7) + data_1 - 0x2000
            if value > 0:
                value = f'+{value}'
            descriptive_str = f'P{port} C{channel:>2} {_TEXT_PITCH_BEND.decode()} {value:>7}'
        elif command == _SYS_SYSEX_START:
            descriptive_str = '' # ignore
        elif command == _SYS_QUARTER_FRAME:
            descriptive_str = f'P{port} {_TEXT_QUARTER_FRAME.decode()} {data_1:>3}    '
        elif command == _SYS_SONG_POSITION:
            value = (data_2 << 7) + data_1
            descriptive_str = f'P{port} {_TEXT_SONG_POSITION.decode()} {value:>7}'
        elif command == _SYS_SONG_SELECT:
            descriptive_str = f'P{port} {_TEXT_SONG_SELECT.decode()} {data_1:>3}    '
        elif command == _SYS_TUNE_REQUEST:
            descriptive_str = f'P{port} {_TEXT_TUNE_REQUEST.decode()}        '
        elif command == _SYS_SYSEX_END:
            descriptive_str = '' # ignore
        elif command == _SYS_CLOCK:
            descriptive_str = f'P{port} {_TEXT_CLOCK.decode()}        '
        elif command == _SYS_START:
            descriptive_str = f'P{port} {_TEXT_START.decode()}        '
        elif command == _SYS_CONTINUE:
            descriptive_str = f'P{port} {_TEXT_CONTINUE.decode()}        '
        elif command == _SYS_STOP:
            descriptive_str = f'P{port} {_TEXT_STOP.decode()}        '
        elif command == _SYS_ACTIVE_SENSING:
            descriptive_str = f'P{port} {_TEXT_ACTIVE_SENSING.decode()}        '
        elif command == _SYS_SYSTEM_RESET:
            descriptive_str = f'P{port} {_TEXT_SYSTEM_RESET.decode()}        '
        else:
            descriptive_str = ''
        if descriptive_str != '':
            data_1_str = '  ' if data_1 == _NONE else f'{data_1:02X}'
            data_2_str = '  ' if data_2 == _NONE else f'{data_2:02X}'
            midi_str = f'[{(command + channel):X} {data_1_str} {data_2_str}]'
        if mode == _MONITOR_MODE_MIDI_IN and descriptive_str != '':
            text_midi_in = f'{descriptive_str} {midi_str}' 
        elif mode == _MONITOR_MODE_MIDI_OUT and descriptive_str != '':
            text_midi_out = f'{descriptive_str} {midi_str}'
        if text_routing != '':
            self.frames[_PAGE_MONITOR].add_to_monitor(_MONITOR_PAGE_ROUTING, text_routing)
        if text_midi_in != '':
            self.frames[_PAGE_MONITOR].add_to_monitor(_MONITOR_PAGE_MIDI_IN, text_midi_in)
        if text_midi_out != '':
            self.frames[_PAGE_MONITOR].add_to_monitor(_MONITOR_PAGE_MIDI_OUT, text_midi_out)

    def delete(self) -> None:
        global ui, display, encoder_0, encoder_1
        del ui
        display.delete() # type: ignore
        encoder_0.close() # type: ignore
        encoder_1.close() # type: ignore
        del encoder_1
        for button in self.buttons:
            button.close()
        del self.buttons

    def _wake_up(self) -> None:
        '''wake up ui; called by self.get_encoder_input and self.process_user_input'''
        self.sleep = False
        self.sleep_time = time.ticks_ms()
        scr.set_display(True) # type: ignore

    def _callback_confirm(self, caller_id: int, confirm: bool) -> None:
        '''callback for confirm pop-up; called (passed on) by self._callback_confirm'''
        _router = router
        if caller_id == _CONFIRM_SAVE:
            if confirm:
                self.pop_ups[_POP_UP_CONFIRM].open(self, _CONFIRM_REPLACE,f'replace {_router.active_program_number + 1:0>3}?', # type: ignore
                                                   self._callback_confirm)
            else:
                next_program = self.next_program
                if next_program != _NONE:
                    _router.update(False, False, False, False, False, False, next_program) # type: ignore
        elif caller_id == _CONFIRM_REPLACE:
            _router.save_active_program(confirm) # type: ignore
            next_program = self.next_program
            if next_program != _NONE:
                if not confirm and next_program > _router.active_program_number: # type: ignore
                    next_program += 1
                _router.update(False, False, False, False, False, False, next_program) # type: ignore

    def _callback_select(self, caller_id: int, selection: int) -> None:
        '''callback for select pop-up; called (passed on) by self.process_user_input'''
        _router = router
        if caller_id == _SELECT_TRIGGER:
            if selection == _NONE or selection == _router.preset_trigger_option: # type: ignore
                return
            #  (6)        12           12      2
            # 111111|000000000000|000000000000|00
            #       |     p      |     d      |i
            #       |     r      |     e      |o
            tmp = -1 * _router.preset_triggers[selection] # type: ignore
            if tmp & 0b11 != _TRIGGER_IN:
                return
            tmp >>= 2
            input_device = tmp & 0xFFF
            input_preset = tmp >> 12
            self.set_trigger(input_device, input_preset)
        elif caller_id == _SELECT_PROGRAM:
            if selection == _NONE or selection == _router.active_program_number: # type: ignore
                return
            if _router.program_changed: # type: ignore
                self.next_program = selection
                self.pop_ups[_POP_UP_CONFIRM].open(self, _CONFIRM_SAVE, 'save changes?', self._callback_confirm)
            else:
                _router.update(False, False, False, False, False, False, selection) # type: ignore

class _Display():
    '''display class; initiated once by ui.__init__'''

    def __init__(self, spi_number: int, cs_pin: int, dc_pin: int, rst_pin: int, backlight_pin: int) -> None:
        global spi, scr
        spi = SPI(spi_number, baudrate=_DISPLAY_BAUTRATE)
        scr = ILI9225(spi, Pin(dc_pin), Pin(cs_pin), Pin(rst_pin), Pin(backlight_pin, mode=Pin.OUT), 3)
        self.font = Font(scr, font)

    def delete(self) -> None:
        global spi, scr
        spi.deinit() # type: ignore
        scr.delete() # type: ignore

def set_user_input_dict(input_dict: dict | None) -> None:
    '''set global user input variable (ui.ui.set_user_input_dict > global user_input_dict > ui.process_user_input >
    Page/PagesTab.process_user_input); called by Page.callback_input and PagesTab.callback_input'''
    global user_input_dict
    user_input_dict = input_dict