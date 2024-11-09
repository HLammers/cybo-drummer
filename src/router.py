''' Router library for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024 Harm Lammers

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

from midi_ports import MIDIPorts
from data_types import GenCurves

_NONE                      = const(-1)

_WAITING_TIME              = const(1) # ms

_MAX_NR_PROGRAMS           = const(255)
_PROGRAM_CHANGE_BLOCK_TIME = const(500) # ms

_MIDI_LEARN_DELAY          = const(300) # ms

_ADD_NEW_LABEL             = '[add new]'
_NEW_PROGRAM               = 'NEW PROGRAM'

_MONITOR_BUFFER_LENGTH     = const(10)

_TRIGGER_IN                = const(1) # start with 1 because used to create negative keys (< 0)
_TRIGGER_OUT               = const(2)

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

    def __init__(self, data, ui, thread_lock) -> None:
        self.data = data
        self.ui = ui
        self.thread_lock = thread_lock
        self.request_wait = False
        self.running = True
        self.active_program_number = _NONE
        self.program_changed = False
        self.is_new_program = False
        self.program = {}
        self.routing = []
        self.routes = {}
        self.input_devices_tuple_all = ()
        self.input_devices_tuple_assigned = ()
        self.output_devices_tuple_all = ()
        self.output_devices_tuple_assigned = ()
        self.input_triggers_tuples = {}
        self.input_triggers_tuple = ()
        self.output_triggers_tuples = {}
        self.input_presets_tuples = {}
        self.input_presets_tuple = ()
        self.output_presets_tuples = {}
        self.output_presets_tuple = ()
        self.input_device_value = 0
        self.input_preset_value = 0
        self.preset_triggers = []
        self.preset_trigger_option = 0
        self.preset_trigger_route = 0
        self.midi_ports = MIDIPorts(thread_lock)
        self.note_off_time_tracker = {}
        self.program_change_time = _NONE
        self.ui_trigger = None
        self._monitor_data = deque((),_MONITOR_BUFFER_LENGTH)
        self._midi_learn_data = None
        self.last_midi_learn_time = _NONE
        self.midi_ports.load()

    def update(self, reload_input_devices: bool = True, reload_output_devices: bool = True, reload_input_triggers: bool = True,
               reload_output_triggers: bool = True, reload_input_presets: bool = True, reload_output_presets: bool = True,
               program_number: int = _NONE, already_waiting: bool = False) -> None:
        '''reload data and call ui.program_change to triggers redraw; called by main_loops.py: init, self._save, self._save_program,
        Page*.process_user_input, Page*.midi_learn, Page*._save_*_settings, Page*._callback_menu, Page*._callback_select'''
        if not already_waiting:
            # request second thread to wait (handshake)
            with self.thread_lock:
                self.request_wait = True
            while self.running:
                time.sleep_ms(_WAITING_TIME)
        # while the second thread is waiting the routing can be updated without thread lock
        _gc_collect = gc.collect
        _gc_threshold = gc.threshold
        _gc_mem_free = gc.mem_free
        _gc_mem_alloc = gc.mem_alloc
        _gc_collect()
        _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())
        self._all_notes_off()
        _data = self.data
        programs = _data.routing_programs
        active_program_number = self.active_program_number
        program = self.program
        if active_program_number != _NONE and (program_number == _NONE or program_number == active_program_number):
            if active_program_number == len(programs): # new program 
                self.is_new_program = True
                active_program_id = _NONE
            else:
                self.is_new_program = False
                active_program_id = programs[active_program_number][1]
        else:
            self.program_changed = False
            if program_number == _NONE:
                program_number = 0
            self.active_program_number = program_number
            if program_number == len(programs): # new program 
                self.is_new_program = True
                active_program_id = _NONE
            else:
                self.is_new_program = False
                active_program_id = programs[program_number][1]
        if self.program_changed:
            program = self.program
        else:
            program = _data.load_program_json_file(active_program_id)
            if program is None:
                program = {'program_change': {}, 'bank_select': {}, 'routing': []}
            self.program = program
        routing = program['routing']
        self.routing = routing
        input_devices_mapping = _data.input_device_mapping
        input_presets = _data.input_presets
        output_presets = _data.output_presets
        input_devices = _data.input_devices
        output_devices = _data.output_devices
        output_devices_mapping = _data.output_device_mapping
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
        midi_learn = settings['midi_learn']
        self.midi_learn = midi_learn
        midi_learn_port = settings['midi_learn_port']
        self.midi_learn_port = midi_learn_port
        self.default_output_velocity = settings['default_output_velocity']
        if reload_input_devices:
            _get_devices_tuple = self._get_devices_tuple
            self.input_devices_tuple_all = _get_devices_tuple(True, True)
            self.input_devices_tuple_assigned = _get_devices_tuple(True, False)
        if reload_output_devices:
            if not reload_input_devices:
                _get_devices_tuple = self._get_devices_tuple
            self.output_devices_tuple_all = _get_devices_tuple(False, True)
            self.output_devices_tuple_assigned = _get_devices_tuple(False, False)
        if reload_input_triggers:
            self.input_triggers_tuples = self._get_triggers_tuples(True)
        if reload_output_triggers:
            self.output_triggers_tuples = self._get_triggers_tuples(False)
        if reload_input_presets:
            self.input_presets_tuples = self._get_presets_tuples(True)
        if reload_output_presets:
            self.output_presets_tuples = self._get_presets_tuples(False)
        input_devices_tuple_assigned = self.input_devices_tuple_assigned
        output_devices_tuple_assigned = self.output_devices_tuple_assigned
        input_presets_tuples = self.input_presets_tuples
        output_presets_tuples = self.output_presets_tuples
        routes = self.routes
        routes.clear()
        triggers = self.preset_triggers
        triggers.clear()
        # set up mapping routes
        for route_number, routing_item in enumerate(routing):
            input_device_name = routing_item['input_device']
            input_device_map = input_devices_mapping[input_device_name]
            input_port = input_device_map['port']
            input_channel = input_device_map['channel']
            input_preset_name = routing_item['input_preset']
            input_preset = input_presets[input_device_name][input_preset_name]
            input_device_mapping = input_devices[input_device_name]['mapping']
            input_device_value = input_devices_tuple_assigned.index(input_device_name)
            input_preset_value = input_presets_tuples[input_device_name].index(input_preset_name)
            output_device_name = routing_item['output_device']
            output_preset_name = routing_item['output_preset']
            if output_preset_name == '':
                continue
            output_preset = output_presets[output_device_name][output_preset_name]            
            output_device = output_devices[output_device_name]
            output_port = output_devices_mapping[output_device_name]['port']
            output_channel = output_device['channel']
            output_device_mapping = output_device['mapping']
            output_device_value = output_devices_tuple_assigned.index(output_device_name)
            output_preset_value = output_presets_tuples[output_device_name].index(output_preset_name)
            output_note = routing_item['note']
            output_note_off = routing_item['note_off']
            for output_map in output_preset['maps']:
                output = output_device_mapping[output_map[0]]
                if output_note == _NONE:
                    output_note = output_map[1]
                output_note_off = output['note_off'] if output_note_off == _NONE else output_note_off - 1
                channel = output['channel']
                if channel != _NONE:
                    output_channel = channel
                for input_map in input_preset['maps']:
                    input = input_device_mapping[input_map]
                    input_note = input['note']
                    pedal_cc = input['pedal_cc']
                    route = {'id': route_number, 'input_trigger': input, 'input_preset': input_preset, 'output_port': output_port,
                                'output_channel': output_channel, 'output_trigger': output, 'output_note': output_note,
                                'curve': GenCurves(output['min_velocity'], output['max_velocity'], output['curve']),
                                'output_note_off': output_note_off, 'cc_value': 0}
                    #         (18)            7     3   3  1
                    # 00000000 00000000 00|1111111|111|111|0
                    #                     |   n   | c | p |
                    #                     |   t   | h | t |0
                    key_int = (input_port << 1) + (input_channel << 4) + (input_note << 7)
                    if not key_int in routes:
                        routes[key_int] = []
                    routes[key_int].append(route)
                    if pedal_cc != _NONE:
                        #         (18)            7     3   3  1
                        # 00000000 00000000 00|1111111|111|111|1
                        #                     |   c   | c | p |
                        #                     |   c   | h | t |1
                        key_int = 1 + (input_port << 1) + (input_channel << 4) + (pedal_cc << 7)
                        if not key_int in routes:
                            routes[key_int] = []
                        routes[key_int].append(route)
                    #  (6)        12           12      2
                    # 111111|000000000000|000000000000|00
                    #       |     p      |     d      |i
                    #       |     r      |     v      |o
                    key_int = -1 * (_TRIGGER_IN + (input_device_value << 2) + (input_preset_value << 14))
                    if not key_int in routes:
                        routes[key_int] = []
                        triggers.append(key_int)
                    routes[key_int].append(route)
                    #  (6)        12           12      2
                    # 111111|000000000000|000000000000|00
                    #       |     p      |     d      |i
                    #       |     r      |     v      |o
                    key_int = -1 * (_TRIGGER_OUT + (output_device_value << 2) + (output_preset_value << 14))
                    if not key_int in routes:
                        routes[key_int] = []
                    routes[key_int].append(route)
        # set device settings
        for device, mapping in output_devices_mapping.items():
            _midi_encoder = self.midi_ports.output_ports[mapping['port']].midi_encoder
            if _midi_encoder != _NONE and device in output_devices:
                device_settings = output_devices[device]
                _midi_encoder.set(device_settings['vel_0_note_off'], device_settings['running_status'])
        # send bank select messages
        bank_select = program['bank_select']
        for device, values in bank_select.items():
            if values != [_NONE, _NONE] and device in output_devices_mapping:
                port = output_devices_mapping[device]['port']
                _midi_encoder = self.midi_ports.output_ports[port].midi_encoder
                if _midi_encoder != _NONE:
                    channel = output_devices[device]['channel']
                    if channel == _NONE:
                        channel = 9 # default drum channel
                    if values[0] != _NONE:
                        _midi_encoder.midi_send(_COMMAND_CC, channel, _CC_BANK_MSB, values[0])
                    if values[1] != _NONE:
                        _midi_encoder.midi_send(_COMMAND_CC, channel, _CC_BANK_LSB, values[1])
        # send program changes
        program_change = program['program_change']
        for device, value in program_change.items():
            if value != _NONE and device in output_devices_mapping:
                port = output_devices_mapping[device]['port']
                _midi_encoder = self.midi_ports.output_ports[port].midi_encoder
                if _midi_encoder != _NONE:
                    channel = output_devices[device]['channel']
                    if channel == _NONE:
                        channel = 9 # default drum channel
                    self.program_change_time = time.ticks_ms() # start blocking receiving progrm change events to avoid them back from output device
                    _midi_encoder.midi_send(_COMMAND_PROGRAM_CHANGE, channel, value, _NONE)
        triggers.sort(reverse=True)
        # set up midi learn route (only having the key in the routes collection matters)
        if midi_learn and midi_learn_port != _NONE:
            routes[f'l{self.midi_learn_port}'] = []
        self.set_trigger()
        _gc_collect()
        _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())
        self.ui.program_change()
        # allow the second thread to continue
        self.running = True

    @micropython.viper
    def process_timed_note_off_events(self):
        '''checks note off time tracker for note off events to be sent; called by main_loops.py: second_thread'''
        note_off_time_tracker = self.note_off_time_tracker
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
            tmp = int(key_int)
            port = tmp & 0b111
            tmp >>= 3
            channel = tmp & 0b1111
            note = tmp >> 4
            _midi_encoder = output_ports[port].midi_encoder
            _midi_encoder.note_off(channel, note)
        for key_int in delete_list:
            del note_off_time_tracker[key_int]

    def process_program_change_break(self) -> None:
        '''set self.program_change_time to _NONE if a blocking time has passed after sending program change message; called
        by main_loops.py: main'''
        if self.program_change_time == _NONE:
            return
        if time.ticks_diff(time.ticks_ms(), self.program_change_time) > _PROGRAM_CHANGE_BLOCK_TIME:
            self.program_change_time = _NONE

    def set_trigger(self, device: int = _NONE, preset: int = _NONE) -> None:
        '''set active trigger (triggered by trigger button) at router level; called by self.update and ui.set_trigger (also calling
        page.set_trigger)'''
        self.preset_trigger_option = 0
        input_devices_tuple_assigned = self.input_devices_tuple_assigned
        self.preset_trigger_route = _NONE
        if device == _NONE and len(input_devices_tuple_assigned) > 0:
            device = self.input_device_value
            if preset == _NONE and len(self.input_presets_tuple) > 0:
                preset = self.input_preset_value
        if 0 <= device < len(input_devices_tuple_assigned):
            device_text = input_devices_tuple_assigned[device]
            self.input_device_value = device
            if self.input_triggers_tuples is not None and device_text in self.input_triggers_tuples:
                self.input_triggers_tuple = self.input_triggers_tuples[device_text]
            else:
                self.input_triggers_tuple = ()
            if self.input_presets_tuples is not None and device_text in self.input_presets_tuples:
                self.input_presets_tuple = self.input_presets_tuples[device_text]
            else:
                self.input_presets_tuple = ()
            if 0 <= preset < len(self.input_presets_tuple):
                preset_text = self.input_presets_tuple[preset]
                self.input_preset_value = preset
                for route_number, route in enumerate(self.routing):
                    if route['input_device'] == device_text and route['input_preset'] == preset_text:
                        self.preset_trigger_route = route_number
                        break
            elif preset == len(self.input_presets_tuple): # new trigger
                self.input_preset_value = _NONE
            else:
                self.input_preset_value = 0
            for trigger_number, key_int in enumerate(self.preset_triggers):
                #  (6)        12           12      2
                # 111111|000000000000|000000000000|00
                #       |     p      |     d      |i
                #       |     r      |     e      |o
                tmp = -1 * key_int
                if tmp & 0b11 != _TRIGGER_IN:
                    continue
                tmp >>= 2
                input_device_value = tmp & 0xFFF
                input_preset_value = tmp >> 12
                if input_device_value == device and input_preset_value == preset:
                    self.preset_trigger_option = trigger_number
                    break
        else:
            self.input_device_value = 0
            self.input_triggers_tuples.clear()
            self.input_triggers_tuple = ()
            self.input_presets_tuples.clear()
            self.input_presets_tuple = ()
            self.input_preset_value = 0
            self.preset_trigger_route = 0

    def trigger(self) -> None:
        '''set global trigger variable when trigger button is pressed; called by ui.process_user_input'''
        #  (6)        12           12      2
        # 111111|000000000000|000000000000|00
        #       |     p      |     d      |i
        #       |     r      |     v      |o
        key_int = -1 * (_TRIGGER_IN + (self.input_device_value << 2) + (self.input_preset_value << 14))
        if key_int in self.routes:
            with self.thread_lock:
                self.ui_trigger = key_int

    def save_active_program(self, replace: bool) -> None:
        '''save active program changes, either replacing or as a new program after the original; called by PageProgram._callback_confirm'''
        # request second thread to wait (handshake)
        with self.thread_lock:
            self.request_wait = True
        while self.running:
            time.sleep_ms(_WAITING_TIME)
        program = self.program
        name = program['name']
        programs = self.data.routing_programs
        if replace:
            id = programs[self.active_program_number][1]
        else:
            id = self._get_new_program_id()
            name = self._check_new_program_name(name)
            self.active_program_number += 1
            programs.insert(self.active_program_number, [name, id])
        self.program_changed = False
        self._save_program()

    def move_active_program(self, destination: int) -> None:
        '''move active program to another program number; called by PageProgram._callback_menu'''
        # request second thread to wait (handshake)
        with self.thread_lock:
            self.request_wait = True
        while self.running:
            time.sleep_ms(_WAITING_TIME)
        programs = self.data.routing_programs
        pos = self.active_program_number        
        if destination > pos:
            destination -= 1
        item = programs.pop(pos)
        programs.insert(destination, item)
        self.active_program_number = destination
        self._save()

    def add_program(self, name: str) -> None:
        '''add program to the end of the list of programs; called by self.delete_active_program, PageProgram.process_user_input and
        PageProgram._callback_text_edit'''
        if name == '' or name == _ADD_NEW_LABEL:
            return
        # request second thread to wait (handshake)
        with self.thread_lock:
            self.request_wait = True
        while self.running:
            time.sleep_ms(_WAITING_TIME)
        id = self._get_new_program_id()
        name = self._check_new_program_name(name)
        programs = self.data.routing_programs
        self.active_program_number = len(programs)
        programs.append([name, id])
        self._save()

    def add_device(self, name: str, is_input: bool) -> None:
        '''add new device to the input or output devices dictionary; called by PageInput._callback_text_edit and
        PageOutput._callback_text_edit'''
        if name == '' or name == _ADD_NEW_LABEL:
            return
        # request second thread to wait (handshake)
        with self.thread_lock:
            self.request_wait = True
        while self.running:
            time.sleep_ms(_WAITING_TIME)
        _data = self.data
        devices = _data.input_devices if is_input else _data.output_devices
        if name in devices:
            # allow the second thread to continue
            self.running = True
            return
        new_device = {'mapping': {}} if is_input else {'channel': _NONE, 'vel_0_note_off': True, 'running_status': True, 'mapping': {}}
        devices[name] = new_device
        self._save(is_input, not is_input)

    def add_trigger(self, device: str, name: str, is_input: bool) -> None:
        '''add new trigger to input or output device’s mapping dictionary; called by PageInput._callback_text_edit and
        PageOutput._callback_text_edit'''
        if name == '' or name == _ADD_NEW_LABEL:
            return
        # request second thread to wait (handshake)
        with self.thread_lock:
            self.request_wait = True
        while self.running:
            time.sleep_ms(_WAITING_TIME)
        _data = self.data
        if is_input:
            if device not in _data.input_devices:
                # allow the second thread to continue
                self.running = True
                return
            triggers = _data.input_devices[device]['mapping']
        else:
            if device not in _data.output_devices:
                # allow the second thread to continue
                self.running = True
                return
            triggers = _data.output_devices[device]['mapping']
        if name in triggers:
            # allow the second thread to continue
            self.running = True
            return
        if is_input:
            triggers[name] = {'note': _NONE, 'pedal_cc': _NONE}
        else:
            triggers[name] = {'channel': _NONE, 'note': _NONE, 'note_off': _NOTE_OFF_OFF, 'threshold': 0, 'curve': 0,
                                'min_velocity': 0, 'max_velocity': 127}
        self._save(reload_input_triggers=is_input, reload_output_triggers=not is_input)

    def add_preset(self, device: str, name: str, is_input: bool) -> None:
        '''add new preset to input or output presets dictionary; called by PageInput._callback_text_edit and PageOutput._callback_text_edit'''
        if name == '' or name == _ADD_NEW_LABEL:
            return
        # request second thread to wait (handshake)
        with self.thread_lock:
            self.request_wait = True
        while self.running:
            time.sleep_ms(_WAITING_TIME)
        _data = self.data
        if is_input:
            if device not in _data.input_devices:
                # allow the second thread to continue
                self.running = True
                return
            all_presets = _data.input_presets
        else:
            if device not in _data.output_devices:
                # allow the second thread to continue
                self.running = True
                return
            all_presets = _data.output_presets
        if device not in all_presets:
            all_presets[device] = {}
        presets = _data.output_presets[device]
        if name in presets:
            # allow the second thread to continue
            self.running = True
            return
        if is_input:
            presets[name] = {'maps': [], 'cc_min': _NONE, 'cc_max': _NONE}
        else:
            presets[name] = {'maps': []}
        self._save(reload_input_presets=is_input, reload_output_presets=not is_input)

    def delete_active_program(self) -> None:
        '''delete active program and add empty program if no program is left in the list of programs; called by PageProgram_callback_confirm'''
        # request second thread to wait (handshake)
        with self.thread_lock:
            self.request_wait = True
        while self.running:
            time.sleep_ms(_WAITING_TIME)
        _data = self.data
        del _data.routing_programs[self.active_program_number]
        if len(_data.routing_programs) == 0:
            self.add_program(_NEW_PROGRAM)
        elif self.active_program_number > 0:
            self.active_program_number -= 1
        self._save()

    def delete_device(self, name: str, is_input: bool) -> None:
        '''delete input or output device from programs, input or output device mapping dictionary, input or output presets dictionary and
            input or output devices dictionary; called by PageInput._callback_confirm and PageOutput._callback_confirm'''
        # request second thread to wait (handshake)
        with self.thread_lock:
            self.request_wait = True
        while self.running:
            time.sleep_ms(_WAITING_TIME)
        _data = self.data
        if is_input:
            device_mapping = _data.input_device_mapping
            presets = _data.input_presets
            devices = _data.input_devices
        else:
            device_mapping = _data.output_device_mapping
            presets = _data.output_presets
            devices = _data.output_devices
        if name not in devices:
            # allow the second thread to continue
            self.running = True
            return
        for program in _data.routing_programs:
            updated_routing = []
            for route in program['routing']:
                if is_input and route['input_device'] != name or not is_input and route['output_device'] != name:
                    updated_routing.append(route)
            program['routing'] = updated_routing
        device_mapping.pop(name, None)
        presets.pop(name, None)
        devices.pop(name, None)
        self._save(is_input, not is_input)

    def delete_trigger(self, device: str, name: str, is_input: bool) -> None:
        '''delete input or output trigger from input or output devices dictionary and input or output presets dictionary; called by
        PageInput._callback_confirm and PageOutput._callback_confirm'''
        # request second thread to wait (handshake)
        with self.thread_lock:
            self.request_wait = True
        while self.running:
            time.sleep_ms(_WAITING_TIME)
        _data = self.data
        if is_input:
            if device not in _data.input_devices:
                # allow the second thread to continue
                self.running = True
                return
            triggers = _data.input_devices[device]['mapping']
            presets = _data.input_presets.get(device, None)
        else:
            if device not in _data.output_devices:
                # allow the second thread to continue
                self.running = True
                return
            triggers = _data.output_devices[device]['mapping']
            presets = _data.output_presets.get(device, None)
        if name not in triggers:
            # allow the second thread to continue
            self.running = True
            return
        triggers.pop(name, None)
        if presets is not None:
            for preset in presets:
                maps = preset['maps']
                updated_maps = []
                for trigger in maps:
                    if trigger != name:
                        updated_maps.append(trigger)
                preset['maps'] = updated_maps
        self._save(reload_input_triggers=is_input, reload_output_triggers=not is_input)

    def delete_preset(self, device: str, name: str, is_input: bool) -> None:
        '''delete input or output preset from input or output presets dictionary; called by PageInput._callback_confirm and
        PageOutput._callback_confirm'''
        # request second thread to wait (handshake)
        with self.thread_lock:
            self.request_wait = True
        while self.running:
            time.sleep_ms(_WAITING_TIME)
        _data = self.data
        if is_input:
            if device not in _data.input_devices:
                # allow the second thread to continue
                self.running = True
                return
            presets = _data.input_presets[device]
        else:
            if device not in _data.output_devices:
                # allow the second thread to continue
                self.running = True
                return
            presets = _data.output_presets[device]
        if name not in presets:
            # allow the second thread to continue
            self.running = True
            return
        for program in _data.routing_programs:
            updated_route = []
            for route in program['routing']:
                if is_input and route['input_device'] != device or not is_input and route['output_device'] != device:
                    updated_route.append(route)
                elif is_input and route['input_preset'] != name or not is_input and route['output_preset'] != name:
                    updated_route.append(route)
            program['routing'] = updated_route
        presets.pop(name, None)
        self._save(reload_input_presets=is_input, reload_output_presets=not is_input)

    def rename_active_program(self, name: str) -> None:
        '''rename active program; called by PageProgram._callback_text_edit'''
        # request second thread to wait (handshake)
        with self.thread_lock:
            self.request_wait = True
        while self.running:
            time.sleep_ms(_WAITING_TIME)
        programs = self.data.routing_programs
        program_number = self.active_program_number
        name = self._check_new_program_name(name, programs[program_number][1])
        programs[program_number][0] = name
        self._save()

    def rename_device(self, old_name: str, new_name: str, is_input: bool) -> None:
        '''rename input or output device in programs, input or output device mapping dictionary, input or output presets dictionary and
        input or output devices dictionary; called by PageInput._callback_text_edit and PageOutput._callback_text_edit'''
        # request second thread to wait (handshake)
        with self.thread_lock:
            self.request_wait = True
        while self.running:
            time.sleep_ms(_WAITING_TIME)
        _data = self.data
        if is_input:
            devices = _data.input_devices
            device_mapping = _data.input_device_mapping
            presets = _data.input_presets
            devices = _data.input_devices
        else:
            devices = _data.output_devices
            device_mapping = _data.output_device_mapping
            presets = _data.output_presets
            devices = _data.output_devices
        if old_name == new_name or old_name not in devices or new_name in devices:
            # allow the second thread to continue
            self.running = True
            return
        field = 'input_device' if is_input else 'output_device'
        _data.change_in_programs(field, old_name, new_name)
        if old_name in device_mapping:
            device_mapping[new_name] = device_mapping.pop(old_name)
        if old_name in presets:
            presets[new_name] = presets.pop(old_name)
        if old_name in devices:
            devices[new_name] = devices.pop(old_name)
        self._save(is_input, not is_input)

    def rename_trigger(self, device: str, old_name: str, new_name: str, is_input: bool) -> None:
        '''rename input or output trigger in input or output devices dictionary and input or output presets dictionary; called by
        PageInput._callback_text_edit and PageOutput._callback_text_edit'''
        # request second thread to wait (handshake)
        with self.thread_lock:
            self.request_wait = True
        while self.running:
            time.sleep_ms(_WAITING_TIME)
        _data = self.data
        if is_input:
            if device not in _data.input_devices:
                # allow the second thread to continue
                self.running = True
                return
            triggers = _data.input_devices[device]['mapping']
            presets = _data.input_presets.get(device, None)
        else:
            if device not in _data.output_devices:
                # allow the second thread to continue
                self.running = True
                return
            triggers = _data.output_devices[device]['mapping']
            presets = _data.output_presets.get(device, None)
        if old_name == new_name or old_name not in triggers or new_name in triggers:
            # allow the second thread to continue
            self.running = True
            return
        if old_name in triggers:
            triggers[new_name] = triggers.pop(old_name)
        if presets is not None:
            for preset in presets:
                maps = preset['maps']
                for i, trigger in enumerate(maps):
                    if trigger == old_name:
                        maps[i] = new_name
        self._save(reload_input_triggers=is_input, reload_output_triggers=not is_input)

    def rename_preset(self, device: str, old_name: str, new_name: str, is_input: bool) -> None:
        '''rename input or output preset in output presets dictionary; called by PageInput._callback_text_edit and
        PageOutput._callback_text_edit'''
        # request second thread to wait (handshake)
        with self.thread_lock:
            self.request_wait = True
        while self.running:
            time.sleep_ms(_WAITING_TIME)
        _data = self.data
        if is_input:
            if device not in _data.input_devices:
                # allow the second thread to continue
                self.running = True
                return
            presets = _data.input_presets[device]
        else:
            if device not in _data.output_devices:
                # allow the second thread to continue
                self.running = True
                return
            presets = _data.output_presets[device]
        if old_name == new_name or old_name not in presets or new_name in presets:
            # allow the second thread to continue
            self.running = True
            return
        field = 'input_preset' if is_input else 'output_preset'
        condition_field = 'input_device' if is_input else 'output_device'
        _data.change_in_programs(field, old_name, new_name, condition_field, device)
        if old_name in presets:
            presets[new_name] = presets.pop(old_name)
        self._save(reload_input_presets=is_input, reload_output_presets=not is_input)

    @micropython.viper
    def route_note_on(self, channel: int, note: int, velocity: int, port: int):
        '''route note on message to assigned destinations; called by MidiDecoder.read'''
        #         (18)            7     3   3  1
        # 00000000 00000000 00|1111111|111|111|0
        #                         n   | c | p |
        #                         t   | h | t |0
        key_int = (port << 1) + (channel << 4) + (note << 7)
        if builtins.int(key_int) in self.routes:
            default_output_velocity = int(self.default_output_velocity)
            output_ports = self.midi_ports.output_ports
            _send_to_monitor = self.send_to_monitor
            for route in self.routes[key_int]:
                input_trigger = route['input_trigger']
                input_preset = route['input_preset']
                output_trigger = route['output_trigger']
                if velocity == 0 and int(route['output_note_off']) == _NOTE_OFF_OFF or velocity < int(output_trigger['threshold']):
                    break
                output_note = int(route['output_note'])
                if output_note == _NONE:            
                    output_note = int(output_trigger['note'])
                if output_note == _NONE:
                    output_note = 60 if note == _NONE else note # 60 == middle C
                velocity = default_output_velocity if velocity == _NONE else int(route['curve'][velocity])
                cc_min = int(input_preset['cc_min'])
                if cc_min == _NONE:
                    cc_min = 0
                cc_max = int(input_preset['cc_max'])
                if cc_max == _NONE:
                    cc_max = 127
                if (note == _NONE or note == int(input_trigger['note'])) and cc_min <= int(route['cc_value']) <= cc_max:
                    output_channel = int(route['output_channel'])
                    output_port = int(route['output_port'])
                    if output_port != _NONE:
                        _midi_encoder = output_ports[output_port].midi_encoder
                        note_off = int(route['output_note_off'])
                        if self._set_note_off(output_port, output_channel, output_note, note_off, _midi_encoder):
                            _midi_encoder.note_on(output_channel, output_note, velocity)
                    _send_to_monitor(_MONITOR_MODE_ROUTING, _NONE, _NONE, _COMMAND_NOTE_ON, _NONE, _NONE, int(route['id']))

    @micropython.viper
    def trigger_note_on(self, output_port: int, output_channel: int, output_note: int, note_off: int):
        '''route note on message to assigned destinations; called by main_loops.py: second_thread'''
        _midi_encoder = self.midi_ports.output_ports[output_port].midi_encoder
        if self._set_note_off(output_port, output_channel, output_note, note_off, _midi_encoder):
            _midi_encoder.note_on(output_channel, output_note, int(self.default_output_velocity))

    def route_note_off(self, channel: int, note: int, velocity: int, port: int) -> None:
        '''route note off message to assigned destinations; called by MidiDecoder.read'''
        return

    @micropython.viper
    def route_midi_thru(self, channel: int, command: int, data_1: int, data_2: int, port: int):
        '''route any kind of midi message to assigned destinations; called by MidiDecoder.read'''
        # midi thru input port -> midi thru output port
        input_channel = int(self.midi_thru_input_channel)
        if bool(self.midi_thru) and int(self.midi_thru_input_port) == port and (input_channel == _NONE or input_channel == channel):
            if channel == _NONE:
                output_channel = _NONE
            else:
                output_channel = int(self.midi_thru_output_channel)
            if output_channel == _NONE:
                output_channel = channel
            _midi_encoder = self.midi_ports.output_ports[int(self.midi_thru_output_port)].midi_encoder
            if type(_midi_encoder) != builtins.int: # _midi_encoder != _NONE
                _midi_encoder.midi_send(command, output_channel, data_1, data_2)
        # route anything else than note on / note off
        #         (18)            7     3   3  1
        # 00000000 00000000 00|1111111|111|111|1
        #                         d   | c | p |
        #                         1   | h | t |1
        key_int = 1 + (port << 1) + (channel << 4) + (data_1 << 7)
        if builtins.int(key_int) in self.routes:
            output_ports = self.midi_ports.output_ports
            _send_to_monitor = self.send_to_monitor
            foot_pedal = False
            for route in self.routes[key_int]:
                if command == _COMMAND_CC and data_1 == int(route['input_trigger']['pedal_cc']):
                    foot_pedal = True
                    route['cc_value'] = data_2
                    output_channel = int(route['output_channel'])
                # _midi_encoder = route['midi_encoder']
                # if type(_midi_encoder) != builtins.int: # _midi_encoder != _NONE
                output_port = int(route['output_port'])
                if output_port != _NONE:
                    _midi_encoder = output_ports[output_port].midi_encoder
                    _midi_encoder.midi_send(command, output_channel, data_1, data_1)
            if foot_pedal:
                _send_to_monitor(_MONITOR_MODE_ROUTING, _NONE, _NONE, _COMMAND_CC, _NONE, data_2, int(route['id']))
        # midi learn (anything except device/trigger)
        if command == _COMMAND_PROGRAM_CHANGE:
            if int(self.program_change_time) == _NONE:
                self._midi_learn_data = self._encode_midi_learn_data(port, channel, _NONE, data_1, _NONE, _NONE, _NONE)
        if not bool(self.midi_learn):
            return
        key_str = f'l{port}'
        if key_str not in self.routes:
            return
        if command == _COMMAND_NOTE_ON:
            self._midi_learn_data = self._encode_midi_learn_data(port, channel, data_1, _NONE, _NONE, _NONE, _NONE)
        elif command == _COMMAND_CC:
            self._midi_learn_data = self._encode_midi_learn_data(port, channel, _NONE, _NONE, data_1, data_2, _NONE)

    def send_to_monitor(self, mode: int, port: int, channel: int = _NONE, command: int = _NONE, data_1: int = _NONE, data_2: int = _NONE,
                        route_number: int = _NONE) -> None:
        '''set monitor data and midi learn data (router.send_to_monitor > router.monitor_data > ui.process_monitor >
        PageMonitor.add_to_monitor); called by self.route_note_on, self.route_note_off, self.route_midi_thru, MidiDecoder.read,
        MidiEncoder.note_on and MidiEncoder.note_off'''
        ###### filtering out system clock and active sensing (TO DO: add filter options setting)
        if command == _SYS_CLOCK or command == _SYS_ACTIVE_SENSING:
            return
        with self.thread_lock:
            self._monitor_data.append(self._encode_monitor_data(mode, port + 1, channel, command, data_1, data_2, route_number))
        if self.midi_learn and route_number != _NONE:
            self._midi_learn_data = self._encode_midi_learn_data(_NONE, _NONE, _NONE, _NONE, _NONE, _NONE, route_number)

    def read_monitor_data(self) -> tuple|None:
        '''return oldest unprocessed monitor data; called by ui.process_monitor_data'''
        with self.thread_lock:
            if len(self._monitor_data) == 0:
                return None
            return self._decode_monitor_data(self._monitor_data.popleft())

    def read_midi_learn_data(self) -> tuple|None:
        '''return unprocessed monitor data if available, otherwise return None; called by main_loops.py: main'''
        with self.thread_lock:
            if self._midi_learn_data is None:
                return None
            now = time.ticks_ms()
            last_time = self.last_midi_learn_time
            if last_time != _NONE and time.ticks_diff(now, last_time) < _MIDI_LEARN_DELAY:
                return None
            self.last_midi_learn_time = now
            values = self._decode_midi_learn_data(self._midi_learn_data)
            self._midi_learn_data = None
            return values

    def delete(self) -> None:
        self.midi_ports.delete()
        del self.input_devices_tuple_all
        del self.input_devices_tuple_assigned
        del self.output_devices_tuple_all
        del self.output_devices_tuple_assigned
        del self.input_triggers_tuples
        del self.input_triggers_tuple
        del self.output_triggers_tuples
        del self.input_presets_tuples
        del self.input_presets_tuple
        del self.output_presets_tuples
        del self.output_presets_tuple
        del self.routing
        del self.program
        del self.routes

    @micropython.viper
    def _get_devices_tuple(self, is_input: bool, include_unassigned: bool):
        '''return tuple with device names; called by self.update'''
        _data = self.data
        if is_input:
            port_mapping = _data.input_device_mapping
            devices = _data.input_devices
            presets = _data.input_presets
        else:
            port_mapping = _data.output_device_mapping
            devices = _data.output_devices
            presets = _data.output_presets
        names = list(devices)
        if not include_unassigned:
            for name in names:
                if not name in presets:
                    names.remove(name)
        values = {}
        for map in names:
            value = int(port_mapping[map]['port']) if map in port_mapping else 255
            if value == _NONE: 
                value = 255
            values[map] = value
        n = int(len(names)) - 1
        while n > 0:
            i = 0
            while i < n:
                if int(values[names[i]]) > int(values[names[i + 1]]):
                    names[i], names[i + 1] = names[i + 1], names[i]
                i += 1
            n -= 1
        return tuple(names)

    @micropython.viper
    def _get_presets_tuples(self, is_input: bool):
        '''return tuple with preset names; called by self.update'''
        output = {}
        _data = self.data
        presets = _data.input_presets if is_input else _data.output_presets
        for device, device_presets in presets.items():
            mapping = _data.input_devices[device]['mapping'] if is_input else _data.output_devices[device]['mapping']
            names = list(device_presets)
            values = {}
            for preset in names:
                value = 128 # one higher than the highest possible note number
                for map in device_presets[preset]['maps']:
                    if is_input:
                        trigger = mapping[map]
                        _value = int(trigger['note'])
                    else:
                        trigger = mapping[map[0]]
                        _value = int(map[1])
                        if _value == _NONE:
                            _value = int(trigger['note'])
                    if _value == _NONE: # and 'channel' in trigger:
                        _value = int(trigger['channel'])
                    if _value != _NONE and _value < value:
                        value = _value
                values[preset] = value
            n = int(len(names)) - 1
            while n > 0:
                i = 0
                while i < n:
                    if int(values[names[i]]) > int(values[names[i + 1]]):
                        names[i], names[i + 1] = names[i + 1], names[i]
                    i += 1
                n -= 1
            output[device] = tuple(names)
        return output

    @micropython.viper
    def _get_triggers_tuples(self, is_input: bool):
        '''return tuple with trigger names; called by self.update'''
        output = {}
        _data = self.data
        devices = _data.input_devices if is_input else _data.output_devices
        for device in devices:
            mapping = devices[device]['mapping']
            names = list(mapping)
            values = {}
            for map in names:
                value = int(mapping[map]['note'])
                if value == _NONE and 'channel' in mapping[map]:
                    value = int(mapping[map]['channel'])
                if value == _NONE: 
                    value = 128 # one higher than the highest possible note number 
                values[map] = value
            n = int(len(names)) - 1
            while n > 0:
                i = 0
                while i < n:
                    if int(values[names[i]]) > int(values[names[i + 1]]):
                        names[i], names[i + 1] = names[i + 1], names[i]
                    i += 1
                n -= 1
            output[device] = tuple(names)
        return output

    def _all_notes_off(self) -> None:
        '''turn off all notes; called by self.update'''
        note_off_time_tracker = self.note_off_time_tracker
        output_ports = self.midi_ports.output_ports
        delete_list = []
        for key_int in note_off_time_tracker:
            delete_list.append(key_int)
            #      (18)               7      4   3
            # 00000000 00000000 00|1111111|1111|111
            #                     |   n   |  c | p
            #                     |   t   |  h | t
            port = key_int & 0b111
            key_int >>= 3
            channel = key_int & 0b1111
            note = key_int >> 4
            _midi_encoder = output_ports[port].midi_encoder
            _midi_encoder.note_off(channel, note)
        for key_int in delete_list:
            del note_off_time_tracker[key_int]

    def _get_new_program_id(self) -> int:
        '''returns the first available program id; called by self.save_active_program and self.add_program'''
        programs = self.data.routing_programs
        existing_ids = (program[1] for program in programs)
        for id in range(_MAX_NR_PROGRAMS):
            if id not in existing_ids:
                return id
        return _NONE

    def _check_new_program_name(self, name: str, id: int = _NONE) -> str:
        '''checks if program name exists and if so adds a number between brackets; called by self.save_active_program, self.add_program
        and self.rename_active_program'''
        programs = self.data.routing_programs
        existing_names = (program[0] for program in programs if program[1] != id)
        if name not in existing_names:
            return name
        new_name = name
        n = 0
        while new_name in existing_names:
            n += 1
            new_name = f'{name} (n)'
        return new_name

    def _save(self, reload_input_devices: bool = False, reload_output_devices: bool = False, reload_input_triggers: bool = False,
              reload_output_triggers: bool = False, reload_input_presets: bool = False, reload_output_presets: bool = False) -> None:
        '''save data set (self.data) and call self.update to trigger reload and redraw; called by
        self.move_active_program, self.add_program, self.add_device, self.add_trigger, self._add_preset, self.delete_active_program,
        self.delete_device, self.delete_trigger, self.delete_preset, self.rename_active_program, self.rename_device, self.rename_trigger
        and self.rename_preset'''
        _data = self.data
        gc.collect()
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
        _data.save_data_json_file()
        _data.load()
        self.update(reload_input_devices, reload_output_devices, reload_input_triggers, reload_output_triggers,
                    reload_input_presets, reload_output_presets, already_waiting=True)

    def _save_program(self) -> None:
        '''save program data (self.program) and call self.update to trigger reload and redraw; called by self.save_active_program'''
        _data = self.data
        gc.collect()
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
        _data.save_program_json_file(self.program, self.data.programs[self.active_program_number][1])
        _data.save_data_json_file()
        _data.load()
        self.update(False, False, False, False, False, False, already_waiting=True)

    @micropython.viper
    def _set_note_off(self, output_port: int, output_channel: int, output_note: int, note_off: int, midi_encoder) -> bool:
        '''add note off to time tracker and return if note on needs to be sent; called by self.route_note_on'''
        if note_off == _NOTE_OFF_OFF:
            return True
        #      (18)               7      4   3
        # 00000000 00000000 00|1111111|1111|111
        #                     |   n   |  c | p
        #                     |   t   |  h | t
        key_int = output_port + (output_channel << 3) + (output_note << 7)
        note_off_time_tracker = self.note_off_time_tracker
        if builtins.int(key_int) in note_off_time_tracker:
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
    def _encode_monitor_data(self, mode: int, port: int, channel: int, command: int, data_1: int, data_2: int, route_number: int):
        '''returns compressed monitor data tuple; called by self.send_to_monitor'''
        #      (14)          8       5    3  2     (8)       8        8        8
        # 00000000 000000|11111111|11111|111|11, 00000000|11111111|11111111|11111111
        #                |   c    |  c  | p |m           |   r    |   d    |   d
        #                |   m    |  h  | t |d           |   t    |   2    |   1
        return mode + (port << 2) + (channel + 1 << 5) + (command + 1 << 10), data_1 + 1 + (data_2 + 1 << 8) + (route_number + 1 << 16)

    @micropython.viper
    def _decode_monitor_data(self, monitor_data):
        '''returns expanded monitor data tuple based on compressed monitor data tuple; called by self.read_monitor_data'''
        monitor_data_0 = int(monitor_data[0])
        monitor_data_1 = int(monitor_data[1])
        #      (14)          8       5    3  2     (8)       8        8        8
        # 00000000 000000|11111111|11111|111|11, 00000000|11111111|11111111|11111111
        #                |   c    |  c  | p |m           |   r    |   d    |   d
        #                |   m    |  h  | t |d           |   t    |   2    |   1
        mode = monitor_data_0 & 0b11
        monitor_data_0 >>= 2
        port = monitor_data_0 & 0b111
        monitor_data_0 >>= 3
        channel = (monitor_data_0 & 0b11111) - 1
        monitor_data_0 >>= 5
        command = monitor_data_0 - 1
        data_1 = (monitor_data_1 & 0b11111111) - 1
        monitor_data_1 >>= 8
        data_2 = (monitor_data_1 & 0b11111111) - 1
        monitor_data_1 >>= 8
        route_number = monitor_data_1 - 1
        return mode, port, channel, command, data_1, data_2, route_number

    @micropython.viper
    def _encode_midi_learn_data(self, port: int, channel: int, note: int, program: int, cc: int, cc_value: int, route_number: int):
        '''returns compressed midi learn data tuple; called by self.route_midi_thru and self.send_to_monitor'''
        #   (8)       8        8       5    3     (8)       8        8        8
        # 00000000|11111111|11111111|11111|111, 00000000|11111111|11111111|11111111
        #         |   p    |   n    |  c  | p           |   r    |   c    |   c
        #         |   r    |   t    |  h  | t           |   t    |   v    |   c
        return port + 1 + (channel + 1 << 3) + (note + 1 << 8) + (program + 1 << 16), cc + 1 + (cc_value + 1 << 8) + (route_number + 1 << 16)

    def _decode_midi_learn_data(self, midi_learn_data):
        '''returns expanded midi learn data tuple based on compressed monitor data tuple; called by ui.process_midi_learn_data'''
        #   (8)       8        8       5    3     (8)       8        8        8
        # 00000000|11111111|11111111|11111|111, 00000000|11111111|11111111|11111111
        #         |   p    |   n    |  c  | p           |   r    |   c    |   c
        #         |   r    |   t    |  h  | t           |   t    |   v    |   c
        monitor_data_0 = int(midi_learn_data[0])
        monitor_data_1 = int(midi_learn_data[1])
        port = (monitor_data_0 & 0b111) - 1
        monitor_data_0 >>= 3
        channel = (monitor_data_0 & 0b11111) - 1
        monitor_data_0 >>= 5
        note = monitor_data_0 - 1
        monitor_data_0 >>= 8
        program = monitor_data_0 - 1
        cc = (monitor_data_1 & 0b11111111) - 1
        monitor_data_1 >>= 8
        cc_value = (monitor_data_1 & 0b11111111) - 1
        monitor_data_1 >>= 8
        route_number = monitor_data_1 - 1
        return port, channel, note, program, cc, cc_value, route_number