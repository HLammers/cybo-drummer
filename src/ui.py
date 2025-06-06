''' Ui library for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024-2025 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

_INITIAL_FRAME      = const(1) # do not set to 0 (pages tab)
ENABLE_SCREEN_DUMPS = const(False)

from machine import Pin, freq
import time

import main_loops as ml
from display import Display
import font
from constants import DEFAULT_PROGRAM_NAME, TRIGGERS

from ui_pages_tabs import PagesTabs
from ui_page_program import PageProgram
from ui_page_matrix import PageMatrix
from ui_page_input import PageInput
from ui_page_output import PageOutput
from ui_page_tools import PageTools
from ui_page_monitor import PageMonitor
from ui_page_settings import PageSettings
from ui_blocks import TextEdit, SelectPopUp, MenuPopUp, ConfirmPopUp, MessagePopUp, \
                      ProgramPopUp, TriggerPopUp, MatrixPopUp, ChordPopUp, AboutPopUp

from encoder import Encoder
from button import Button

import midi_tools as mt

_NONE                        = const(-1)

_ASCII_A                     = const(65)

_DISPLAY_BAUTRATE            = const(100_000_000) # display specs: 50_000_000; max: _OVERCLOCK_FREQ / 2

_SLEEP_TIME_OUT              = const(600_000) # ms

# no longer needed once machine.lightsleep has been fixed in a future version of micropython
_HIGH_FREQ                   = const(300_000_000) # Hz
_LOW_FREQ                    = const(48_000_000) # Hz

_ENCODER_NAV_PIN_A           = const(15)
_ENCODER_NAV_PIN_B           = const(14)
_ENCODER_VAL_PIN_A           = const(26)
_ENCODER_VAL_PIN_B           = const(27)

_BUTTON_DEL_PIN              = const(28) # NAV encoder button
_BUTTON_SEL_OPT_PIN          = const(22) # VAL encoder button
_BUTTON_TRIGGER_YES_PIN      = const(2)
_BUTTON_PAGE_NO_PIN          = const(3)
_BUTTON_PROG_PIN             = const(16)
_BUTTON_PINS                 = (_BUTTON_DEL_PIN, _BUTTON_SEL_OPT_PIN, _BUTTON_TRIGGER_YES_PIN, _BUTTON_PAGE_NO_PIN, _BUTTON_PROG_PIN)

_BUTTON_DEL                  = const(0) # NAV encoder button
_BUTTON_SEL_OPT              = const(1) # VAL encoder button
_BUTTON_TRIGGER_YES          = const(2)
_BUTTON_PAGE_NO              = const(3)
_BUTTON_PROGRAM              = const(4)

_BUTTON_EVENT_PRESS          = const(1)
_BUTTON_EVENT_LONG_PRESS     = const(2)

_ENCODER_NAV                 = const(0)
_ENCODER_VAL                 = const(1)

_DISPLAY_SPI                 = const(0)
# _DISPLAY_PIN_MOSI            = const(19) # SDI
_DISPLAY_PIN_DC              = const(20) # RS
_DISPLAY_PIN_RST             = const(21)
_DISPLAY_PIN_BACKLIGHT       = const(17) # LED
_DISPLAY_W                   = const(220)
_DISPLAY_H                   = const(176)

_FRAME_PAGE_SELECT           = const(0)
_FRAME_PROGRAM               = const(1)
_FRAME_MATRIX                = const(2)
_FRAME_INPUT                 = const(3)
_FRAME_OUTPUT                = const(4)
_FRAME_TOOLS                 = const(5)
_FRAME_MONITOR               = const(6)
_FRAME_SETTINGS              = const(7)

_POP_UP_TEXT_EDIT            = const(0)
_POP_UP_SELECT               = const(1)
_POP_UP_MENU                 = const(2)
_POP_UP_CONFIRM              = const(3)
_POP_UP_MESSAGE              = const(4)
_POP_UP_PROGRAM              = const(5)
_POP_UP_TRIGGER              = const(6)
_POP_UP_MATRIX               = const(7)
_POP_UP_CHORD                = const(8)
_POP_UP_ABOUT                = const(9)

_CONFIRM_SAVE                = const(0)
_CONFIRM_REPLACE_PROGRAM     = const(1)
_TEXT_EDIT                   = const(0)

_MARGIN                      = const(3)
_PAGES_W                     = const(16)

_MAX_CHARACTERS              = const(34)

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

_CC_BANK_LSB                 = const(0x20)

_TEXT_NOTE_OFF               = 'NoteOff '
_TEXT_NOTE_ON                = 'NoteOn  '
_TEXT_POLYPHONIC_PRESSURE    = 'PolyPres'
_TEXT_CC                     = 'ContCtrl'
_TEXT_PROGRAM_CHANGE         = 'ProgChng'
_TEXT_CHANNEL_PRESSURE       = 'ChanPres'
_TEXT_PITCH_BEND             = 'PtchBend'
_TEXT_QUARTER_FRAME          = 'SC Qrtr Frme'
_TEXT_SONG_POSITION          = 'SC Song Pos '
_TEXT_SONG_SELECT            = 'SC Song Slct'
_TEXT_TUNE_REQUEST           = 'SC Tune Req '
_TEXT_CLOCK                  = 'SR Clock    '
_TEXT_START                  = 'SR Start    '
_TEXT_CONTINUE               = 'SR Continue '
_TEXT_STOP                   = 'SR Stop     '
_TEXT_ACTIVE_SENSING         = 'SR Act Sens '
_TEXT_SYSTEM_RESET           = 'SR Sys Reset'

class UI():
    '''user interface class; initiated once by main_loops.py: init'''

    def __init__(self) -> None:
        self.display = Display(_DISPLAY_SPI, _DISPLAY_BAUTRATE, Pin(_DISPLAY_PIN_DC), Pin(_DISPLAY_PIN_RST),
                          Pin(_DISPLAY_PIN_BACKLIGHT, mode=Pin.OUT), font)
        self.encoder_nav = Encoder(_ENCODER_NAV_PIN_A, _ENCODER_NAV_PIN_B, div=4)
        self.encoder_val = Encoder(_ENCODER_VAL_PIN_A, _ENCODER_VAL_PIN_B, div=4)
        self.buttons = (buttons := [Button(pin) for pin in _BUTTON_PINS])
        buttons[_BUTTON_TRIGGER_YES].long_press = True
        buttons[_BUTTON_SEL_OPT].long_press = True
        buttons[_BUTTON_PROGRAM].long_press = True
        self.user_input_tuple = None
        self.page_select_mode = False
        self.trigger_timer = None
        self.frames = []
        self.active_frame = _INITIAL_FRAME
        self.frames.append(PagesTabs(_FRAME_PAGE_SELECT, _DISPLAY_W - _PAGES_W, 0, _PAGES_W, _DISPLAY_H, _INITIAL_FRAME))
        x, y, w, h = 0, 0, _DISPLAY_W - _PAGES_W - _MARGIN, _DISPLAY_H
        self.frames.append(PageProgram(_FRAME_PROGRAM, x, y, w, h, self.active_frame == _FRAME_PROGRAM))
        self.frames.append(PageMatrix(_FRAME_MATRIX, x, y, w, h, self.active_frame == _FRAME_MATRIX))
        self.frames.append(PageInput(_FRAME_INPUT, x, y, w, h, self.active_frame == _FRAME_INPUT))
        self.frames.append(PageOutput(_FRAME_OUTPUT, x, y, w, h, self.active_frame == _FRAME_OUTPUT))
        self.frames.append(PageTools(_FRAME_TOOLS, x, y, w, h, self.active_frame == _FRAME_TOOLS))
        self.frames.append(PageMonitor(_FRAME_MONITOR, x, y, w, h, self.active_frame == _FRAME_MONITOR))
        self.frames.append(PageSettings(_FRAME_SETTINGS, x, y, w, h, self.active_frame == _FRAME_SETTINGS))
        self.pop_ups = []
        self.pop_ups.append(TextEdit(_POP_UP_TEXT_EDIT))
        self.pop_ups.append(SelectPopUp(_POP_UP_SELECT))
        self.pop_ups.append(MenuPopUp(_POP_UP_MENU))
        self.pop_ups.append(ConfirmPopUp(_POP_UP_CONFIRM))
        self.pop_ups.append(MessagePopUp(_POP_UP_MESSAGE))
        self.pop_ups.append(ProgramPopUp(_POP_UP_PROGRAM))
        self.pop_ups.append(TriggerPopUp(_POP_UP_TRIGGER))
        self.pop_ups.append(MatrixPopUp(_POP_UP_MATRIX))
        self.pop_ups.append(ChordPopUp(_POP_UP_CHORD))
        self.pop_ups.append(AboutPopUp(_POP_UP_ABOUT))
        self.active_pop_up = None
        self.sleep = False
        self.sleep_time = time.ticks_ms()

    def check_sleep_time_out(self):
        '''check if enough time has passed to put ui to sleep, called by main_loops.py: main'''
        if not self.sleep and time.ticks_diff(time.ticks_ms(), self.sleep_time) > _SLEEP_TIME_OUT:
            self.sleep = True
            self.display.set_display(False)
            # use machine.lightsleep once it has been fixed in a future version of micropython
            # lightsleep()
            freq(_LOW_FREQ)

    def program_change(self, update_only: bool) -> None:
        '''update ui after program change; called by router.update'''
        for frame in self.frames:
            frame.program_change(update_only)

    def set_trigger(self, trigger: int = _NONE, zone: int = _NONE) -> None:
        '''set active trigger (triggered by the trigger button), call router.set_trigger and page.set_trigger; called by
        self._callback_trigger, PageProgram.midi_learn, PageProgram._callback_trigger, PageProgram._callback_matrix,
        PageProgram.midi_learn, PageInput.midi_learn and PageInput._callback_trigger'''
        ml.router.set_trigger(trigger, zone)
        self.frames[self.active_frame].set_trigger()

    def process_encoder_input(self) -> bool:
        '''process encoder input (ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder); called by
        main_loops.py: main'''
        redraw = False
        value_nav = self.encoder_nav.value()
        value_val = self.encoder_val.value()
        if value_nav != _NONE or value_val != _NONE:
            self._wake_up()
        if value_nav != _NONE:
            if self.active_pop_up is None:
                redraw |= self.frames[self.active_frame].encoder(_ENCODER_NAV, value_nav, self.page_select_mode) # type: ignore
            else: # pop-up visible
                redraw |= self.active_pop_up.encoder(_ENCODER_NAV, value_nav)
        if value_val != _NONE:
            if self.active_pop_up is None:
                if self.page_select_mode:
                    self.frames[_FRAME_PAGE_SELECT].set_page(value_val)
                    redraw = True
                else:
                    redraw |= self.frames[self.active_frame].encoder(_ENCODER_VAL, value_val, self.page_select_mode)
            else: # pop-up visible
                redraw |= self.active_pop_up.encoder(_ENCODER_VAL, value_val)
        return redraw

    def process_user_input(self) -> bool:
        '''process buttons and other user input (ui.set_user_input_tuple > ui.user_input_tuple > ui.process_user_input >
        Page/PagesTab.process_user_input); called by main_loops.py: main'''
        redraw = False
        if (user_input_tuple := self.user_input_tuple) is not None:
            self._wake_up()
            frame_id, block_id, value, button_del, button_sel_opt = user_input_tuple
            self.user_input_tuple = None
            redraw |= self.frames[frame_id].process_user_input(block_id, value, button_del, button_sel_opt)
        _router = ml.router
        _wake_up = self._wake_up
        _active_pop_up = self.active_pop_up
        for button_id, button in enumerate(self.buttons):
            if not (value := button.value()):
                continue
            _wake_up()
            if button_id == _BUTTON_DEL:
                if _active_pop_up is None:
                    if self.page_select_mode:
                        self.page_select_mode = False
                        frames = self.frames
                        frames[self.active_frame].set_page_encoders(False)
                        frames[_FRAME_PAGE_SELECT].set_page_encoders(False)
                        redraw = True
                    else:
                        redraw |= self.frames[self.active_frame].button_del(value)
                else: # pop-up visible
                    redraw |= _active_pop_up.button_del()
            elif button_id == _BUTTON_SEL_OPT:
                if _active_pop_up is None:
                    if self.page_select_mode:
                        self.page_select_mode = False
                        frames = self.frames
                        frames[self.active_frame].set_page_encoders(False)
                        frames[_FRAME_PAGE_SELECT].set_page_encoders(False)
                        redraw = True
                    else:
                        redraw |= self.frames[self.active_frame].button_sel_opt(value)
                else: # pop-up visible
                    redraw |= _active_pop_up.button_sel_opt()
            elif button_id == _BUTTON_TRIGGER_YES:
                if _active_pop_up is None:
                    if not (page_select_mode := self.page_select_mode) and value == _BUTTON_EVENT_PRESS: # short-press of trigger button and not in page select mode
                        _router.trigger()
                    elif value == _BUTTON_EVENT_LONG_PRESS: # long-press of trigger button
                        if page_select_mode:
                            self.page_select_mode = False
                            self.frames[self.active_frame].set_page_encoders(False)
                            self.frames[_FRAME_PAGE_SELECT].set_page_encoders(False)
                        self.pop_ups[_POP_UP_TRIGGER].open(self.frames[self.active_frame], _NONE, self._callback_trigger)
                        redraw = True
                elif value == _BUTTON_EVENT_PRESS and _active_pop_up.button_yes(): # pop-up visible, short-press of trigger button
                    self.frames[self.active_frame].restore()
                    redraw = True
            elif button_id == _BUTTON_PAGE_NO:
                if _active_pop_up is None:
                    page_pressed = not self.page_select_mode
                    self.page_select_mode = page_pressed
                    self.frames[self.active_frame].set_page_encoders(page_pressed)
                    self.frames[_FRAME_PAGE_SELECT].set_page_encoders(page_pressed)
                    redraw = True
                elif value == _BUTTON_EVENT_PRESS and _active_pop_up.button_no(): # pop-up visible, short-press of page button
                    self.frames[self.active_frame].restore()
                    redraw = True
            else: # button_id == _BUTTON_PROGRAM
                if value == _BUTTON_EVENT_LONG_PRESS:
                    self.display.save_screen_dump()
                elif _BUTTON_EVENT_PRESS and _active_pop_up is None: # pop-up not visible, short-press of program button
                    if self.page_select_mode:
                        self.page_select_mode = False
                        self.frames[self.active_frame].set_page_encoders(False)
                        self.frames[_FRAME_PAGE_SELECT].set_page_encoders(False)
                    if _router.program_changed:
                        self.save_program()
                    else:
                        self.pop_ups[_POP_UP_PROGRAM].open(self.frames[self.active_frame], ('select bank', 'select program'),
                                                        _router.active_bank, _router.active_program, self._callback_program_select)
                    redraw = True
        return redraw

    def process_midi_learn_data(self, midi_learn_data) -> bool:
        '''process midi learn data (router.send_to_monitor > router.midi_learn_data > ui.process_midi_learn_data > Page.midi_learn); called by
        main_loops.py: main'''
        port, channel, trigger, zone, note, program, cc, cc_value = midi_learn_data
        if self.frames[self.active_frame].midi_learn(port, channel, trigger, zone, note, program, cc, cc_value):
            return True
        else:
            _router = ml.router
            if cc_value != _NONE and cc == _CC_BANK_LSB and _router.active_bank != cc_value:
                if _router.program_changed:
                    self.save_program(cc_value, 0)
                else:
                    _router.update(cc_value)
                return True
            elif program != _NONE and _router.active_program != program:
                if _router.program_changed:
                    self.save_program(_router.active_bank, program)
                else:
                    _router.update(program_number=program)
                return True
            return False

    def process_monitor(self) -> bool:
        '''process monitor data (router.send_to_monitor > router.monitor_data > ui.process_monitor > PageMonitor.add_to_monitor); called by
        main_loops.py: main'''
        _ml = ml
        _router = _ml.router
        if (monitor_data := _router.read_monitor_data()) is None:
            return False
        self._wake_up()
        mode, input_port, channel, trigger, zone, output_port, voice, command, data_1, data_2 = monitor_data
        text_routing = ''
        text_midi_in = ''
        text_midi_out = ''
        if trigger != _NONE:
            _data = _ml.data
            input_device_text = _data.input_port_mapping[input_port][0]
            if command == _COMMAND_NOTE_ON:
                trigger_defs = TRIGGERS[trigger]
                trigger_text = f'{trigger_defs[0]}{trigger_defs[2][0][zone]}'
                input = f'{input_device_text} {trigger_text}'
                output_device_text = _data.output_mapping[2 * output_port]
                voice_text = _data.output_mapping[2 * output_port + 1]['mapping'][voice * 2][0]
                output = f'{output_device_text} {voice_text}'
                l = len(text_routing := f'{input} > {output}')
                if l > _MAX_CHARACTERS:
                    d = l - _MAX_CHARACTERS
                    if (l_input := len(input)) > (l_output := len(output)):
                        d_out = (d * l_output) // (l - 3)
                        d_in = d - d_out
                    else:
                        d_in = (d * l_input) // (l - 3)
                        d_out = d - d_in
                    if d_in > 0:
                        input_device_text = input_device_text[:(len(input_device_text) - d_in)]
                    if d_out > 0:
                        output_device_text = output_device_text[:(len(output_device_text) - d_out)]
                    text_routing = f'{input_device_text} {trigger_text} > {output_device_text} {voice_text}'    
            elif command == _COMMAND_CC:
                text_pedal = f' foot pedal {data_2}'
                text_routing = f'{input_device_text}{text_pedal}'
                l = len(text_routing)
                if l > _MAX_CHARACTERS:
                    input_device_text = input_device_text[:(_MAX_CHARACTERS - len(text_pedal))]
                    text_routing = f'{input_device_text}{text_pedal}'
        if command == _COMMAND_NOTE_OFF:
            data_1_str = '' if data_1 == _NONE else mt.number_to_note(data_1)
            data_2_str = '' if data_2 == _NONE else str(data_2)
            descriptive_str = f'P{input_port} C{channel:>2} {_TEXT_NOTE_OFF} {data_1_str:>3} {data_2_str:>3}'
        elif command == _COMMAND_NOTE_ON:
            data_1_str = '' if data_1 == _NONE else mt.number_to_note(data_1)
            data_2_str = '' if data_2 == _NONE else str(data_2)
            descriptive_str = f'P{input_port} C{channel:>2} {_TEXT_NOTE_ON} {data_1_str:>3} {data_2_str:>3}'
        elif command == _COMMAND_POLYPHONIC_PRESSURE:
            descriptive_str = f'P{input_port} C{channel:>2} {_TEXT_POLYPHONIC_PRESSURE} {data_1:>3} {data_2:>3}'
        elif command == _COMMAND_CC:
            descriptive_str = f'P{input_port} C{channel:>2} {_TEXT_CC} {data_1:>3} {data_2:>3}'
        elif command == _COMMAND_PROGRAM_CHANGE:
            descriptive_str = f'P{input_port} C{channel:>2} {_TEXT_PROGRAM_CHANGE} {data_1:>3}    '
        elif command == _COMMAND_CHANNEL_PRESSURE:
            descriptive_str = f'P{input_port} C{channel:>2} {_TEXT_CHANNEL_PRESSURE} {data_1:>3}    '
        elif command == _COMMAND_PITCH_BEND:
            if (value := (data_2 << 7) + data_1 - 0x2000) > 0:
                value = f'+{value}'
            descriptive_str = f'P{input_port} C{channel:>2} {_TEXT_PITCH_BEND} {value:>7}'
        elif command == _SYS_SYSEX_START:
            descriptive_str = '' # ignore
        elif command == _SYS_QUARTER_FRAME:
            descriptive_str = f'P{input_port} {_TEXT_QUARTER_FRAME} {data_1:>3}    '
        elif command == _SYS_SONG_POSITION:
            value = (data_2 << 7) + data_1
            descriptive_str = f'P{input_port} {_TEXT_SONG_POSITION} {value:>7}'
        elif command == _SYS_SONG_SELECT:
            descriptive_str = f'P{input_port} {_TEXT_SONG_SELECT} {data_1:>3}    '
        elif command == _SYS_TUNE_REQUEST:
            descriptive_str = f'P{input_port} {_TEXT_TUNE_REQUEST}        '
        elif command == _SYS_SYSEX_END:
            descriptive_str = '' # ignore
        elif command == _SYS_CLOCK:
            descriptive_str = f'P{input_port} {_TEXT_CLOCK}        '
        elif command == _SYS_START:
            descriptive_str = f'P{input_port} {_TEXT_START}        '
        elif command == _SYS_CONTINUE:
            descriptive_str = f'P{input_port} {_TEXT_CONTINUE}        '
        elif command == _SYS_STOP:
            descriptive_str = f'P{input_port} {_TEXT_STOP}        '
        elif command == _SYS_ACTIVE_SENSING:
            descriptive_str = f'P{input_port} {_TEXT_ACTIVE_SENSING}        '
        elif command == _SYS_SYSTEM_RESET:
            descriptive_str = f'P{input_port} {_TEXT_SYSTEM_RESET}        '
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
        redraw = False
        if text_routing != '':
            redraw |= self.frames[_FRAME_MONITOR].add_to_monitor(_MONITOR_PAGE_ROUTING, text_routing)
        if text_midi_in != '':
            redraw |= self.frames[_FRAME_MONITOR].add_to_monitor(_MONITOR_PAGE_MIDI_IN, text_midi_in)
        if text_midi_out != '':
            redraw |= self.frames[_FRAME_MONITOR].add_to_monitor(_MONITOR_PAGE_MIDI_OUT, text_midi_out)
        return redraw

    def set_user_input_tuple(self, input_tuple: tuple|None) -> None:
        '''set global user input variable (ui.set_user_input_tuple > ui.user_input_tuple > ui.process_user_input >
        Page/PagesTab.process_user_input); called by Page.callback_input and PagesTab.callback_input'''
        self.user_input_tuple = input_tuple

    def save_program(self, and_set_bank: int = _NONE, and_set_program: int = _NONE) -> None:
        '''initiate process to save program and set bank/program afterwards; called by self.process_user_input,
        self.process_midi_learn_data, self._callback_program_select and PageProgram.process_user_input
        
        save_program -> _callback_program_save -> _save_program_confirm                 # PROGRAM button pressed
                     -> _callback_confirm (save) -> _save_program_confirm               # Program change
            
            _save_program_confirm -> _save_program                                      # Save current program
                                  -> _callback_confirm (replace) -> _save_program       # Replace existing program position
                                                                 -> _callback_program_save -> _save_program_confirm
                                  -> _callback_text_edit -> _save_program               # Save new program or existing one
                                                                                        # to unused program position
        '''
        self.and_set = (and_set_bank, and_set_program)
        if and_set_bank == _NONE:
            _router = ml.router
            self.pop_ups[_POP_UP_PROGRAM].open(self.frames[self.active_frame], ('bank to save to', 'program to save to'),
                                               _router.active_bank, _router.active_program, self._callback_program_save)
        else:
            self.pop_ups[_POP_UP_CONFIRM].open(self.frames[self.active_frame], _CONFIRM_SAVE, 'save changes?', self._callback_confirm)

    def delete(self) -> None:
        self.display.delete()
        self.encoder_nav.close()
        self.encoder_val.close()
        for button in self.buttons:
            button.close()
        del self.buttons

    def _save_program_confirm(self, to_bank: int, to_program: int) -> None:
        '''second step in process to save program and set bank/program afterwards; called by self._callback_program_save and
        self._callback_confirm'''
        _ml = ml
        _data = _ml.data
        _router = _ml.router
        self.save_to = (to_bank, to_program)
        if to_bank in (programs := _data.programs) and to_program in programs[to_bank]: # save to existing program position
            if to_bank == _router.active_bank and to_program == _router.active_program: # save current program
                self._save_program()
            else:
                frame = self.frames[self.active_frame]
                frame.draw()
                self.pop_ups[_POP_UP_CONFIRM].open(frame, _CONFIRM_REPLACE_PROGRAM, f'replace {chr(_ASCII_A + to_bank)}{to_program:0>2}?',
                                                   self._callback_confirm)
        else: # save new program or existing one to unused program position
            frame = self.frames[self.active_frame]
            frame.draw()
            if (active_bank := _router.active_bank) in programs and (active_program := _router.active_program) in programs[active_bank]:
               name = programs[active_bank][active_program]
            else:
                name = ''
            self.pop_ups[_POP_UP_TEXT_EDIT].open(frame, _TEXT_EDIT, name, is_file_name=True, callback_func=self._callback_text_edit)

    def _save_program(self, text: str = '') -> None:
        '''final step in process to save program and set bank/program afterwards; called by self._save_program_confirm,
        self._callback_text_edit and self._callback_confirm'''
        _router = ml.router
        _router.save_program(*self.save_to, text)
        _router.update(*self.and_set)

    def _wake_up(self) -> None:
        '''wake up ui; called by self.process_encoder_input, self.process_user_input and self.process_monitor'''
        if self.sleep:
            # no longer needed once machine.lightsleep has been fixed in a future version of micropython
            freq(_HIGH_FREQ)
            self.display.set_display(True)
        self.sleep = False
        self.sleep_time = time.ticks_ms()

    def _callback_program_select(self, bank: int, program: int) -> None:
        '''callback for program select pop-up; called (passed on) by self.process_user_input'''
        _router = ml.router
        if bank == _router.active_bank and program == _router.active_program:
            return
        if _router.program_changed:
            self.frames[self.active_frame].draw()
            self.save_program(bank, program)
        else:
            _router.update(bank, program)

    def _callback_program_save(self, bank: int, program: int) -> None:
        '''callback for program save pop-up; called (passed on) by self.save_program and self._callback_confirm'''
        self.and_set = (bank, program)
        self.frames[self.active_frame].draw()
        self._save_program_confirm(bank, program)

    def _callback_trigger(self, trigger: int, zone: int) -> None:
        '''callback for trigger select pop-up; called (passed on) by self.process_user_input'''
        self.set_trigger(trigger, zone)

    def _callback_text_edit(self, caller_id: int, text: str) -> None:
        '''callback function for text edit pop-up; called (passed on) by self._save_program_confirm'''
        if text == '':
            text = DEFAULT_PROGRAM_NAME
        self._save_program(text)

    def _callback_confirm(self, caller_id: int, confirm: bool) -> None:
        '''callback for confirm pop-up; called (passed on) by self.save_program and self._save_program_confirm'''
        _ml = ml
        _router = _ml.router
        if caller_id == _CONFIRM_SAVE:
            if confirm:
                self._save_program_confirm(_router.active_bank, _router.active_program)
            else:
                _router.update()
        else: # caller_id == _CONFIRM_REPLACE_PROGRAM
            if confirm:
                self._save_program()
            else:
                frame = self.frames[self.active_frame]
                frame.draw()
                self.pop_ups[_POP_UP_PROGRAM].open(self.frames[self.active_frame], ('bank to save to', 'program to save to'),
                                                   _router.active_bank, _router.active_program, self._callback_program_save)