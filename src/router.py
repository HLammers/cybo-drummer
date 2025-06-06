''' Router library for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024-2025 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
    
    Some minor concepts of this code are inspired by:
        Simple MIDI Multi-RX-TX Router, copyright (c) 2023 diyelectromusic (Kevin),
        https://github.com/diyelectromusic/, https://diyelectromusic.com/'''

import micropython
import builtins
from collections import deque
import gc
import time

import main_loops as ml
from midi_ports import MIDIPorts
from data_types import GenCurves
from constants import BLANK_LABEL, TRIGGERS, TRIGGERS_SHORT

_NONE                      = const(-1)

_ASCII_A                   = const(65)

_FRAME_INPUT               = const(2)

_MAX_VOICES                = const(64)
_MATRIX_ROWS               = const(8)
_MATRIX_COLUMNS            = const(8)

_PROGRAM_CHANGE_BLOCK_TIME = const(500) # ms
_MIDI_LEARN_DELAY          = const(300) # ms

_ADD_NEW_LABEL             = '[add new]'

_MONITOR_BUFFER_LENGTH     = const(10)

_MONITOR_MODE_ROUTING      = const(2)

# _COMMAND_NOTE_OFF          = const(0x80)
_COMMAND_NOTE_ON           = const(0x90)
_COMMAND_CC                = const(0xB0)
_COMMAND_PROGRAM_CHANGE    = const(0xC0)
_SYS_CLOCK                 = const(0xF8)
_SYS_ACTIVE_SENSING        = const(0xFE)
_CC_BANK_MSB               = const(0x00)
_CC_BANK_LSB               = const(0x20)

_NOTE_OFF_OFF              = const(-1) 
_NOTE_OFF_PULSE            = const(0)
_NOTE_OFF_TOGGLE           = const(1)
_NOTE_OFF_OFFSET_MS        = const(77)

class Router():
    '''router class; initiated once by main_loops.py: init'''

    def __init__(self) -> None:
        self.start_second_thread = False
        self.terminated = False
        self.request_wait = False
        self.running = True
        self.active_bank = 0
        self.active_program = 0
        self.program_changed = False
        self.program = {}
        self.trigger_matrix = [[-1, -1, -1, -1, -1, -1, -1, -1],
                               [-1, -1, -1, -1, -1, -1, -1, -1],
                               [-1, -1, -1, -1, -1, -1, -1, -1],
                               [-1, -1, -1, -1, -1, -1, -1, -1],
                               [-1, -1, -1, -1, -1, -1, -1, -1],
                               [-1, -1, -1, -1, -1, -1, -1, -1],
                               [-1, -1, -1, -1, -1, -1, -1, -1],
                               [-1, -1, -1, -1, -1, -1, -1, -1]]
        self.trigger_zones = [[0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0],
                              [0, 0, 0, 0, 0, 0, 0, 0]]
        self.routing = []
        self.routes = {}
        self.input_trigger = 0
        input_triggers = ml.data.input_triggers
        for i, trigger_short in enumerate(TRIGGERS_SHORT):
            if trigger_short in input_triggers:
                self.input_trigger = i
                break
        self.input_zone = 0
        self.midi_ports = MIDIPorts(ml.thread_lock)
        self.note_off_time_tracker = {}
        self.program_change_time = _NONE
        self.ui_trigger = None
        self._monitor_data = deque((),_MONITOR_BUFFER_LENGTH)
        self._midi_learn_data = None
        self.last_midi_learn_time = _NONE
        self.midi_ports.load()

    def update(self, bank: int = _NONE, program_number: int = _NONE, already_waiting: bool = False) -> None:
        '''reload data and call ui.program_change to triggers redraw; called by main_loops.py: init, self._save, self._save_program,
        ui._callback_select, Page*.process_user_input, Page*._save_*_settings, Page*._callback_menu, Page*._callback_select'''
        _ml = ml
        if not already_waiting:
            self.handshake() # request second thread to wait
        # while the second thread is waiting the routing can be updated without thread lock
        _gc = gc
        _gc_collect = _gc.collect
        _gc_threshold = _gc.threshold
        _gc_mem_free = _gc.mem_free
        _gc_mem_alloc = _gc.mem_alloc
        _gc_collect()
        _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())
        self._all_notes_off()
        _data = _ml.data
        program = self.program
        if bank == _NONE:
            bank = self.active_bank
        else:
            self.active_bank = bank
        if program_number == _NONE:
            update_only = True
            program_number = self.active_program
        else:
            if not (update_only := self.active_program == program_number):
                self.active_program = program_number
        if self.program_changed:
            program = self.program
        else:
            trigger_matrix = self.trigger_matrix
            stored_matrix = _data.trigger_matrix
            for i in range(_MATRIX_ROWS):
                for j in range(_MATRIX_COLUMNS):
                    trigger_matrix[i][j] = stored_matrix[i][j] # type: ignore
            self.program = (program := _data.load_program_json_file(bank, program_number))
        self.routing = (routing := program['routing'])
        input_port_mapping = _data.input_port_mapping
        input_triggers = _data.input_triggers
        output_mapping = _data.output_mapping
        settings = _data.settings
        midi_thru_input_port = settings['midi_thru_input_port']
        midi_thru_input_channel = settings['midi_thru_input_channel']
        midi_thru_output_port = settings['midi_thru_output_port']
        midi_thru_output_channel = settings['midi_thru_output_channel']
        midi_thru = False if midi_thru_input_port == _NONE or midi_thru_output_port == _NONE else settings['midi_thru']
        if midi_thru:
            self.midi_thru = True
            self.midi_thru_input_port = midi_thru_input_port
            self.midi_thru_input_channel = midi_thru_input_channel
            self.midi_thru_output_port = midi_thru_output_port
            self.midi_thru_output_channel = midi_thru_output_channel
        else:
            self.midi_thru = False
            self.midi_thru_input_channel = _NONE
        self.midi_learn = (midi_learn := settings['midi_learn'])
        self.midi_learn_port = (midi_learn_port := settings['midi_learn_port'])
        self.default_output_velocity = settings['default_output_velocity']
        triggers_short = TRIGGERS_SHORT
        routes = self.routes
        routes.clear()
        # set up mapping routes
        for routing_item in routing:
            trigger = triggers_short.index(trigger_name := routing_item['trigger'])
            try:
                input = input_triggers[trigger_name]
            except:
                continue
            input_mapping = input['mapping'][(zone := routing_item['zone'])]
            if (input_port := input['port']) == _NONE:
                continue
            for layer in routing_item['layers'].values():
                if (voice := layer['voice']) == '':
                    continue
                output_device = output_mapping[2 * (output_port := layer['output_port']) + 1]
                output_channel = output_device['channel']
                if voice in (output_device_mapping := output_device['mapping']):
                    voice_map = output_device_mapping[(voice := output_device_mapping.index(voice)) + 1]
                    if (output_note := layer['note']) == _NONE:
                        output_note = voice_map['note']
                    if (note_off := layer['note_off']) == _NOTE_OFF_OFF:
                        note_off = voice_map['note_off']
                    if (channel := voice_map['channel']) != _NONE:
                        output_channel = channel
                    route = {'trigger': trigger, 'zone': zone, 'input_defs': input_mapping, 'output_port': output_port, 'voice': voice // 2,
                             'output_channel': output_channel, 'output_note': output_note, 'note_off': note_off, 'cc_value': 0,
                             'curve': GenCurves(voice_map['min_velocity'], voice_map['max_velocity'], voice_map['curve'], voice_map['threshold'],
                                                layer['transient'], layer['transient_layer'], layer['scale'])}
                    #         (18)            7     3   3  1
                    # 00000000 00000000 00|1111111|111|111|0
                    #                     |   n   | c | p |
                    #                     |   t   | h | t |0
                    key_int = (input_port << 1) + ((input_channel := input_port_mapping[input_port][1]) << 4) + (input_mapping['note'] << 7)
                    if not key_int in routes:
                        routes[key_int] = []
                    routes[key_int].append(route)
                    if (pedal_cc := input_mapping['pedal_cc']) != _NONE:
                        #         (18)            7     3   3  1
                        # 00000000 00000000 00|1111111|111|111|1
                        #                     |   c   | c | p |
                        #                     |   c   | h | t |1
                        if not (key_int := 1 + (input_port << 1) + (input_channel << 4) + (pedal_cc << 7)) in routes:
                            routes[key_int] = []
                        routes[key_int].append(route)
                    #          (22)             7     3
                    # 1111111111111111111111|0000000|000
                    #                       |   t   | z
                    #                       |   r   | n
                    if not (key_int := -1 * (zone + 1 + (trigger + 1 << 7))) in routes:
                        routes[key_int] = []
                    routes[key_int].append(route)
        # set device settings
        for i in range(len(output_mapping) // 2):
            if (_midi_encoder := self.midi_ports.output_ports[i].midi_encoder) != _NONE:
                device_settings = output_mapping[2 * i + 1]
                _midi_encoder.set(device_settings['vel_0_note_off'], device_settings['running_status'])
        # send bank select messages
        bank_select = program['bank_select']
        for i in range(len(bank_select) // 2):
            if (values := bank_select[2 * i + 1]) != [_NONE, _NONE]:
                port = bank_select[2 * i]
                if (_midi_encoder := self.midi_ports.output_ports[port].midi_encoder) != _NONE:
                    if (channel := output_mapping[2 * port + 1]['channel']) == _NONE:
                        channel = 9 # default drum channel
                    if values[0] != _NONE:
                        _midi_encoder.midi_send(_COMMAND_CC, channel, _CC_BANK_MSB, values[0])
                    if values[1] != _NONE:
                        _midi_encoder.midi_send(_COMMAND_CC, channel, _CC_BANK_LSB, values[1])
        # send program changes
        program_change = program['program_change']
        for i in range(len(program_change) // 2):
            if (value := program_change[2 * i + 1]) != _NONE:
                port = program_change[2 * i]
                if (_midi_encoder := self.midi_ports.output_ports[port].midi_encoder) != _NONE:
                    if (channel := output_mapping[2 * port + 1]['channel']) == _NONE:
                        channel = 9 # default drum channel
                    # start blocking receiving progrm change events to avoid them back from output device
                    self.program_change_time = time.ticks_ms()
                    _midi_encoder.midi_send(_COMMAND_PROGRAM_CHANGE, channel, value, _NONE)
        # set up midi learn route (only having the key in the routes collection matters)
        if midi_learn and midi_learn_port != _NONE:
            routes[f'l{self.midi_learn_port}'] = []
        self.set_trigger()
        _gc_collect()
        _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())
        _ml.ui.program_change(update_only)
        self.resume() # resume second thread

    def handshake(self):
        '''request second thread to wait (handshake); called by self.update, self.set_trigger, self.save_*, self.move_*, self.delete_*,
        self.rename_*, self.add_voice, Page*._save_*_settings, PageTools.initiate_* and PageSettings.process_user_input'''
        if not self.start_second_thread:
            return
        with ml.thread_lock:
            self.request_wait = True
        while self.running:
            pass

    def resume(self):
        '''allow second thread to resume running; called by Page*._save_*_settings, PageTools.initiate_* and PageSettings.process_user_input'''
        with ml.thread_lock:
            self.running = True

    @micropython.viper
    def process_timed_note_off_events(self):
        '''checks note off time tracker for note off events to be sent; called by main_loops.py: second_thread'''
        if int(len(note_off_time_tracker := self.note_off_time_tracker)) == 0:
            return
        _time = time
        _ticks_diff = _time.ticks_diff
        _ticks_ms = _time.ticks_ms
        output_ports = self.midi_ports.output_ports
        delete_list = []
        for key_int, time_value in note_off_time_tracker.items():
            if int(time_value) == _NONE or int(_ticks_diff(_ticks_ms(), time_value)) < 0:
                continue
            delete_list.append(key_int)
            #      (18)               7      4   3
            # 00000000 00000000 00|1111111|1111|111
            #                     |   n   |  c | p
            #                     |   t   |  h | t
            port = (tmp := int(key_int)) & 0b111
            tmp >>= 3
            channel = tmp & 0b1111
            _midi_encoder = output_ports[port].midi_encoder
            _midi_encoder.note_off(channel, tmp >> 4) # note = tmp >> 4
        for key_int in delete_list:
            del note_off_time_tracker[key_int]

    def process_program_change_break(self) -> None:
        '''set self.program_change_time to _NONE if a blocking time has passed after sending program change message; called
        by main_loops.py: main'''
        if (program_change_time := self.program_change_time) == _NONE:
            return
        if time.ticks_diff(time.ticks_ms(), program_change_time) > _PROGRAM_CHANGE_BLOCK_TIME:
            self.program_change_time = _NONE

    def set_trigger(self, trigger: int = _NONE, zone: int = _NONE) -> None:
        '''set active trigger (triggered by trigger button) at router level; called by self.update and ui.set_trigger (also calling
        page.set_trigger)'''
        self.handshake() # request second thread to wait
        if trigger == _NONE:
            trigger = self.input_trigger
            if zone == _NONE:
                zone = self.input_zone
        self.input_trigger = trigger
        if zone < 0 or zone >= len(TRIGGERS[trigger][2]):
            zone = 0
        self.input_zone = zone
        trigger_matrix = self.trigger_matrix
        found = False
        for i in range(_MATRIX_ROWS):
            for j in range(_MATRIX_COLUMNS):
                if trigger_matrix[i][j] == trigger:
                    self.trigger_zones[i][j] = zone
                    found = True
                    break
            if found:
                break
        self.resume() # resume second thread

    def trigger(self) -> None:
        '''set global trigger variable when trigger button is pressed; called by ui.process_user_input'''
        #          (22)             7     3
        # 1111111111111111111111|0000000|000
        #                       |   t   | z
        #                       |   r   | n
        if (key_int := -1 * (self.input_zone + 1 + (self.input_trigger + 1 << 7))) in self.routes:
            with ml.thread_lock:
                self.ui_trigger = key_int

    def save_program(self, bank: int, program: int, name: str = '') -> None:
        '''save active program changes; called by ui._callback_text_edit and ui._callback_confirm'''
        self.handshake() # request second thread to wait
        _data = ml.data
        if name != '':
            if bank in (programs := _data.programs):
                bank_programs = programs[bank]
            else:
                bank_programs = {}
                programs[bank] = bank_programs
            bank_programs[program] = name
        self.program_changed = False
        _gc = gc
        _gc.collect()
        _gc.threshold(_gc.mem_free() // 4 + _gc.mem_alloc())
        _data.save_program_json_file(self.program, bank, program)
        _data.save_data_json_file()
        _data.load()
        self.update(already_waiting=True)

    def move_program(self, to_bank: int, to_program: int) -> None:
        '''move active program to another program number; called by PageProgram._callback_menu'''
        if (from_bank := self.active_bank) == to_bank and self.active_program == to_program:
            self.update()
            return
        _ml = ml
        self.handshake() # request second thread to wait
        self.active_bank, self.active_program = _ml.data.move_program(from_bank, self.active_bank, to_bank, to_program)
        self._save()

    def delete_program(self) -> None:
        '''delete active program or shift programs if the active program is an empty slot; called by PageProgram_callback_confirm'''
        _ml = ml
        self.handshake() # request second thread to wait
        _data = _ml.data
        try:
            name = _data.programs[self.active_bank][self.active_program]
        except:
            name = ''
        _data.delete_program(self.active_bank, self.active_program, name)
        self._save()

    def rename_program(self, new_name: str) -> None:
        '''rename active program; called by PageProgram._callback_text_edit'''
        _ml = ml
        _data = _ml.data
        try:
            old_name = _data.programs[(bank := self.active_bank)][(program := self.active_program)]
        except:
            old_name = ''
        if new_name == old_name:
            self.update()
            return
        self.handshake() # request second thread to wait
        _data.rename_program(bank, program, new_name)
        self._save()

    def move_voice(self, port: int, source: int, destination: int) -> None:
        '''move voice to another place in the list of voices and return result position; called by PageOutput._callback_menu and
        PageOutput._callback_select'''
        if source == destination:
            self.update()
            return
        _ml = ml
        self.handshake() # request second thread to wait
        mapping = _ml.data.output_mapping[2 * port + 1]['mapping']
        if destination > source:
            destination -= 1
        name = mapping.pop(2 * source)
        mapping.insert(2 * destination, mapping.pop(2 * source))
        mapping.insert(2 * destination, name)
        self._save()

    def add_voice(self, port: int, name: str) -> None:
        '''add new voice to output mapping list; called by PageOutput._callback_text_edit'''
        _ml = ml
        voices = _ml.data.output_mapping[2 * port + 1]['mapping']
        if name == '' or name == _ADD_NEW_LABEL or len(voices) == 2 * _MAX_VOICES:
            self.update()
            return
        self.handshake() # request second thread to wait
        voices.append(self._check_name(voices, name))
        voices.append({'channel': _NONE, 'note': _NONE, 'note_off': _NOTE_OFF_OFF, 'threshold': 0, 'curve': 0,
                       'min_velocity': 0, 'max_velocity': 127})
        self._save()

    def delete_voice(self, port: int, name: str) -> None:
        '''delete voice from output mapping list dictionary; called by PageOutput._callback_confirm'''
        _ml = ml
        if name not in (voices := _ml.data.output_mapping[2 * port + 1]['mapping']):
            self.update()
            return
        self.handshake() # request second thread to wait
        del voices[(n := voices.index(name)) + 1]
        del voices[n]
        self._save()

    def rename_voice(self, port: int, old_name: str, new_name: str) -> None:
        '''rename voice in output mapping list; called by PageOutput._callback_text_edit'''
        _ml = ml
        _data = _ml.data
        voices = _data.output_mapping[2 * port + 1]['mapping']
        if old_name == new_name or old_name not in voices:
            self.update()
            return
        self.handshake() # request second thread to wait
        new_name = self._check_name(voices, new_name, old_name)
        voices[voices.index(old_name)] = new_name
        _data.change_in_programs('voice', old_name, new_name, 'output_port', port)
        self._save()

    @micropython.viper
    def route_note_on(self, channel: int, note: int, velocity: int, port: int):
        '''route note on message to assigned destinations; called by MidiDecoder.read'''
        #         (18)            7     3   3  1
        # 00000000 00000000 00|1111111|111|111|0
        #                         n   | c | p |
        #                         t   | h | t |0
        if builtins.int(key_int := (port << 1) + (channel << 4) + (note << 7)) in self.routes:
            default_output_velocity = int(self.default_output_velocity)
            output_ports = self.midi_ports.output_ports
            _send_to_monitor = self.send_to_monitor
            for route in self.routes[key_int]:
                if velocity == 0 and int(route['note_off']) == _NOTE_OFF_OFF:
                    break
                output_note = int(route['output_note'])
                if output_note == _NONE:
                    output_note = 60 if note == _NONE else note # 60 == middle C
                velocity = default_output_velocity if velocity == _NONE else int(route['curve'][velocity])
                if velocity == 0:
                    break
                input_defs = route['input_defs']
                if (cc_min := int(input_defs['cc_min'])) == _NONE:
                    cc_min = 0
                if (cc_max := int(input_defs['cc_max'])) == _NONE:
                    cc_max = 127
                if (note == _NONE or note == int(input_defs['note'])) and cc_min <= int(route['cc_value']) <= cc_max:
                    if (output_port := int(route['output_port'])) != _NONE:
                        output_channel = int(route['output_channel'])
                        note_off = int(route['note_off'])
                        _midi_encoder = output_ports[output_port].midi_encoder
                        if self._set_note_off(output_port, output_channel, output_note, note_off, _midi_encoder):
                            _midi_encoder.note_on(output_channel, output_note, velocity)
                    _send_to_monitor(_MONITOR_MODE_ROUTING, trigger=route['trigger'], zone=route['zone'],
                                     output_port=output_port, voice=route['voice'], command=_COMMAND_NOTE_ON)

    def trigger_note_on(self, output_port: int, output_channel: int, output_note: int, note_off: int) -> None:
        '''route note on message to assigned destinations; called by main_loops.py: second_thread'''
        _midi_encoder = self.midi_ports.output_ports[output_port].midi_encoder
        if self._set_note_off(output_port, output_channel, output_note, note_off, _midi_encoder):
            _midi_encoder.note_on(output_channel, output_note, int(self.default_output_velocity))

    @micropython.viper
    def route_midi_thru(self, channel: int, command: int, data_1: int, data_2: int, port: int):
        '''route any kind of midi message to assigned destinations; called by MidiDecoder.read'''
        # midi thru input port -> midi thru output port
        input_channel = int(self.midi_thru_input_channel)
        if bool(self.midi_thru) and int(self.midi_thru_input_port) == port and (input_channel == _NONE or input_channel == channel):
            output_channel = _NONE if channel == _NONE else int(self.midi_thru_output_channel)
            if output_channel == _NONE:
                output_channel = channel
            if type(_midi_encoder := self.midi_ports.output_ports[int(self.midi_thru_output_port)].midi_encoder) != builtins.int:
                _midi_encoder.midi_send(command, output_channel, data_1, data_2)
        # route anything else than note on / note off
        #         (18)            7     3   3  1
        # 00000000 00000000 00|1111111|111|111|1
        #                         d   | c | p |
        #                         1   | h | t |1
        if builtins.int(key_int := 1 + (port << 1) + (channel << 4) + (data_1 << 7)) in self.routes:
            output_ports = self.midi_ports.output_ports
            for route in self.routes[key_int]:
                output_port = int(route['output_port'])
                if command == _COMMAND_CC and data_1 == int(route['input_defs']['pedal_cc']):
                    route['cc_value'] = data_2
                    output_channel = int(route['output_channel'])
                    self.send_to_monitor(_MONITOR_MODE_ROUTING, trigger=int(route['trigger']), zone=int(route['zone']),
                                         output_port=output_port, voice=route['voice'], command=_COMMAND_CC, data_2=data_2)
                if output_port != _NONE:
                    output_ports[output_port].midi_encoder.midi_send(command, output_channel, data_1, data_1)
        # midi learn (anything except device/trigger)
        if command == _COMMAND_PROGRAM_CHANGE:
            if int(self.program_change_time) == _NONE:
                midi_learn_data = self._encode_midi_learn_data(port, channel, _NONE, _NONE, _NONE, data_1, _NONE, _NONE)
                with ml.thread_lock:
                    self._midi_learn_data = midi_learn_data
###### TO BE DOCUMENTED: MIDI LEARN ALSO WORKS ON SELECTED PORT FOR INPUT PAGE, NOT ON MIDI LEARN PORT
        if int(ml.ui.active_frame) != _FRAME_INPUT and (not bool(self.midi_learn) or f'l{port}' not in self.routes):
            return
        if command == _COMMAND_NOTE_ON:
            midi_learn_data = self._encode_midi_learn_data(port, channel, _NONE, _NONE, data_1, _NONE, _NONE, _NONE)
            with ml.thread_lock:
                self._midi_learn_data = midi_learn_data
        elif command == _COMMAND_CC:
            midi_learn_data = self._encode_midi_learn_data(port, channel, _NONE, _NONE, _NONE, _NONE, data_1, data_2)
            with ml.thread_lock:
                self._midi_learn_data = midi_learn_data

    def send_to_monitor(self, mode: int, input_port: int = _NONE, channel: int = _NONE, trigger: int = _NONE, zone: int = _NONE,
                        output_port: int = _NONE, voice: int = _NONE,
                        command: int = _NONE, data_1: int = _NONE, data_2: int = _NONE) -> None:
        '''set monitor data and midi learn data (router.send_to_monitor > router.monitor_data > ui.process_monitor >
        PageMonitor.add_to_monitor); called by self.route_note_on, self.route_note_off, self.route_midi_thru, MidiDecoder.read,
        MidiEncoder.note_on and MidiEncoder.note_off'''
        ###### filtering out system clock and active sensing (TO DO: add filter options setting)
        if command == _SYS_CLOCK or command == _SYS_ACTIVE_SENSING:
            return
        _thread_lock = ml.thread_lock
        monitor_data = self._encode_monitor_data(mode, input_port + 1, trigger, zone, channel, output_port, voice, command, data_1, data_2)
        with _thread_lock:
            self._monitor_data.append(monitor_data)
        if self.midi_learn and trigger != _NONE:
            midi_learn_data = self._encode_midi_learn_data(_NONE, _NONE, trigger, zone, _NONE, _NONE, _NONE, _NONE)
            with _thread_lock:
                self._midi_learn_data = midi_learn_data

    def read_monitor_data(self) -> tuple|None:
        '''return oldest unprocessed monitor data; called by ui.process_monitor'''
        if len(self._monitor_data) == 0:
            return None
        with ml.thread_lock:
            monitor_data = self._monitor_data.popleft()
        return self._decode_monitor_data(monitor_data)

    def read_midi_learn_data(self) -> tuple|None:
        '''return unprocessed monitor data if available, otherwise return None; called by main_loops.py: main'''
        if (_midi_learn_data := self._midi_learn_data) is None:
            return None
        now = time.ticks_ms()
        last_time = self.last_midi_learn_time
        if last_time != _NONE and time.ticks_diff(now, last_time) < _MIDI_LEARN_DELAY:
            return None
        self.last_midi_learn_time = now
        decoded_data = self._decode_midi_learn_data(_midi_learn_data)
        with ml.thread_lock:
            self._midi_learn_data = None
        return decoded_data

    def program_options(self, i: int) -> str:
        '''function to pass on to program options generator; also called by PageMatrix._set_matrix_page_options'''
        bank = self.active_bank
        prefix = f'{chr(_ASCII_A + bank)}{i:02} '
        try:
            return prefix + ml.data.programs[bank][i]
        except:
            return prefix + BLANK_LABEL

    def delete(self) -> None:
        self.midi_ports.delete()
        del self.routing
        del self.program
        del self.routes

    def _all_notes_off(self) -> None:
        '''turn off all notes; called by self.update'''
        output_ports = self.midi_ports.output_ports
        delete_list = []
        for key_int in (note_off_time_tracker := self.note_off_time_tracker):
            delete_list.append(key_int)
            #      (18)               7      4   3
            # 00000000 00000000 00|1111111|1111|111
            #                     |   n   |  c | p
            #                     |   t   |  h | t
            _midi_encoder = output_ports[key_int & 0b111].midi_encoder
            key_int >>= 3
            _midi_encoder.note_off(key_int & 0b1111, key_int >> 4) # channel, note
        for key_int in delete_list:
            del note_off_time_tracker[key_int]

    def _check_name(self, in_list: list|tuple, new_name: str, old_name: str = '') -> str:
        '''checks if program name exists and if so adds a number between brackets; called by self.add_voice and self.rename_voice'''
        existing_names = (name for name in in_list if name != old_name)
        _name = new_name
        if _name not in existing_names:
            del existing_names
            return new_name
        name = new_name
        n = 0
        while _name in existing_names:
            n += 1
            new_name = f'{name} (n)'
            _name = new_name
        del existing_names
        return new_name

    def _save(self) -> None:
        '''save data set and call self.update to trigger reload and redraw; called by self.move_program, self.add_voice, self.delete_program,
        self.delete_voice, self.rename_program, self.rename_device and self.rename_voice'''
        _data = ml.data
        _gc = gc
        _gc.collect()
        _gc.threshold(_gc.mem_free() // 4 + _gc.mem_alloc())
        _data.save_data_json_file()
        _data.load()
        self.update(already_waiting=True)

    @micropython.viper
    def _set_note_off(self, output_port: int, output_channel: int, output_note: int, note_off: int, midi_encoder) -> bool:
        '''add note off to time tracker and return if note on needs to be sent; called by self.route_note_on'''
        if note_off == _NOTE_OFF_OFF:
            return True
        #      (18)               7      4   3
        # 00000000 00000000 00|1111111|1111|111
        #                     |   n   |  c | p
        #                     |   t   |  h | t
        note_off_time_tracker = self.note_off_time_tracker
        if builtins.int(key_int := output_port + (output_channel << 3) + (output_note << 7)) in note_off_time_tracker:
            midi_encoder.note_off(output_channel, output_note)
            if note_off == _NOTE_OFF_TOGGLE:
                del note_off_time_tracker[builtins.int(key_int)]
                return False
        if note_off == _NOTE_OFF_PULSE:
            time_value = int(time.ticks_ms())
        elif note_off == _NOTE_OFF_TOGGLE:
            time_value = _NONE
        else:
            _time = time
            time_value = int(_time.ticks_add(_time.ticks_ms(), note_off + _NOTE_OFF_OFFSET_MS))
        note_off_time_tracker[key_int] = time_value
        return True

    @micropython.viper
    def _encode_monitor_data(self, mode: int, input_port: int, trigger: int, zone: int, channel: int, output_port: int, voice: int,
                             command: int, data_1: int, data_2: int):
        '''returns compressed monitor data tuple; called by self.send_to_monitor'''
        #    7     3   4      8       5    3  2     (8)       8        8        8
        # 0000000|111|1111|11111111|11111|111|11, 00000000|11111111|11111111|11111111
        #    v   | o | z  |   t    |  c  | i |m           |   d    |   d    |   c
        #    c   | p | n  |   r    |  h  | p |d           |   2    |   1    |   m
        return mode + (input_port << 2) + (channel + 1 << 5) + (trigger + 1 << 10) + (zone + 1 << 18) + \
               (output_port + 1 << 22) + (voice + 1 << 25), command + 1 + (data_1 + 1 << 8) + (data_2 + 1 << 16)

    @micropython.viper
    def _decode_monitor_data(self, monitor_data):
        '''returns expanded monitor data tuple based on compressed monitor data tuple; called by self.read_monitor_data'''
        #    7     3   4      8       5    3  2     (8)       8        8        8
        # 0000000|111|1111|11111111|11111|111|11, 00000000|11111111|11111111|11111111
        #    v   | o | z  |   t    |  c  | i |m           |   d    |   d    |   c
        #    c   | p | n  |   r    |  h  | p |d           |   2    |   1    |   m
        mode = (monitor_data_0 := int(monitor_data[0])) & 0b11
        monitor_data_0 >>= 2
        input_port = monitor_data_0 & 0b111
        monitor_data_0 >>= 3
        channel = (monitor_data_0 & 0b11111) - 1
        monitor_data_0 >>= 5
        trigger = (monitor_data_0 & 0b11111111) - 1
        monitor_data_0 >>= 8
        zone = (monitor_data_0 & 0b1111) - 1
        monitor_data_0 >>= 4
        output_port = (monitor_data_0 & 0b111) - 1
        monitor_data_0 >>= 3
        voice = monitor_data_0 - 1
        command = ((monitor_data_1 := int(monitor_data[1])) & 0b11111111) - 1
        monitor_data_1 >>= 8
        data_1 = (monitor_data_1 & 0b11111111) - 1
        monitor_data_1 >>= 8
        data_2 = monitor_data_1 - 1
        return mode, input_port, channel, trigger, zone, output_port, voice, command, data_1, data_2

    @micropython.viper
    def _encode_midi_learn_data(self, port: int, channel: int, trigger: int, zone: int, note: int, program: int, cc: int, cc_value: int):
        '''returns compressed midi learn data tuple; called by self.route_midi_thru and self.send_to_monitor'''
        #   (12)        8      8       5    3      8        8        8        8
        # 000000000000|1111|11111111|11111|111, 11111111|11111111|11111111|11111111
        #             | z  |   t    |  c  | p      c    |   c    |   p    |   n
        #             | n  |   r    |  h  | t      v    |   c    |   r    |   t
        return (port + 1 + (channel + 1 << 3) + (trigger + 1 << 8) + (zone + 1 << 16),
                note + 1 + (program + 1 << 8) + (cc + 1 << 16) + (cc_value + 1 << 24))

    def _decode_midi_learn_data(self, midi_learn_data):
        '''returns expanded midi learn data tuple based on compressed monitor data tuple; called by ui.process_midi_learn_data'''
        #   (12)        8      8       5    3      8        8        8        8
        # 000000000000|1111|11111111|11111|111, 11111111|11111111|11111111|11111111
        #             | z  |   t    |  c  | p      c    |   c    |   p    |   n
        #             | n  |   r    |  h  | t      v    |   c    |   r    |   t
        port = ((monitor_data_0 := int(midi_learn_data[0])) & 0b111) - 1
        monitor_data_0 >>= 3
        channel = (monitor_data_0 & 0b11111) - 1
        monitor_data_0 >>= 5
        trigger = (monitor_data_0 & 0b11111111) - 1
        monitor_data_0 >>= 8
        zone = monitor_data_0 - 1
        note = ((monitor_data_1 := int(midi_learn_data[1])) & 0b11111111) - 1
        monitor_data_1 >>= 8
        program = (monitor_data_1 & 0b11111111) - 1
        monitor_data_1 >>= 8
        cc = (monitor_data_1 & 0b11111111) - 1
        monitor_data_1 >>= 8
        cc_value = monitor_data_1 - 1
        return port, channel, trigger, zone, note, program, cc, cc_value