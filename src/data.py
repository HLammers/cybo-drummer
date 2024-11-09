''' Library providing data class for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

import os
import json
import gc

_NONE = const(-1)

class Data:
    '''overall data class for routing, definitions and settings; initiated once in main_loops.py: init'''

    def __init__(self, ui, thread_lock) -> None:
        self.ui = ui
        self.thread_lock = thread_lock
        self.data = {}                  # full data set, as stored in json file
        self.routing_programs = []      # array of programs
        self.input_device_mapping = {}  # mapping collection of input devices to midi in ports and channels
        self.output_device_mapping = {} # mapping collection of output devices to midi out ports
        self.input_presets = {}         # mapping collection input devices/presets to (foot pedal) cc values and one or more output triggers
        self.output_presets = {}        # mapping collection of output devices/presets to one or more output triggers
        self.input_devices = {}         # trigger definitions for input devices
        self.output_devices = {}        # output device definitions and trigger definitions for output devices
        self.settings = {}              # collection of global settings
        self.programs_tuple = ()        # tuple of program names

    def load_data_json_file(self, file: str = 'data.json') -> bool:
        '''load data set (self.data) from json file and return True if successful; called by main_loops.py: init and self.restore_back_up'''
        reset = False
        with self.thread_lock:
            try:
                data_file = open(f'/data_files/{file}')
                self.data = json.load(data_file)
                data_file.close()
            except:
                if file != 'data.json':
                    return False
                reset = True
                try:
                    os.mkdir('data_files')
                except:
                    pass
                try:
                    os.mkdir('data_files/programs')
                except:
                    pass
                try:
                    os.mkdir('data_files/programs_bak')
                except:
                    pass
        if reset:
            self.factory_reset()
        else:
            self.load()
        return True

    def load_program_json_file(self, id: int) -> dict|None:
        '''return program data_files from json file; called by router.update'''
        if id == _NONE:
            return
        try:
            file = open(f'/data_files/programs/program_{id}.json')
            return_data = json.load(file)
            file.close()
            return return_data
        except:
            return

    def save_data_json_file(self, file: str = 'data.json') -> None:
        '''save data set (self.data) to json file; called by self.save_back_up, router._save, router._save_program, Page*._save_*_settings
        or Page*.process_user_input and Page*.midi_learn'''
        data_file = open(f'/data_files/{file}', 'w')
        json.dump(self.data, data_file)
        data_file.close()

    def save_program_json_file(self, program_data: dict, id: int) -> None:
        '''save program data to json file; called by router._save_program'''
        file = open(f'/data_files/programs/program_{id}.json', 'w')
        with self.thread_lock:
            json.dump(program_data, file)
        file.close()

    def save_back_up(self) -> None:
        '''save data set (self.data) to /data_files/back_up.json and program files to /data_files/programs_bak/; called by
        PageSettings._callback_confirm'''
        self.save_data_json_file('/data_files/back_up.json')
        _gc_collect = gc.collect
        _gc_threshold = gc.threshold
        _gc_mem_free = gc.mem_free
        _gc_mem_alloc = gc.mem_alloc
        _gc_collect()
        _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())
        with self.thread_lock:
            files = os.listdir('/data_files/programs_bak')
            for file in files:
                os.remove(f'/data_files/programs_bak/{file}')
            files = os.listdir('/data_files/programs')
            for file in files:
                file = open(f'/data_files/programs/{file}')
                data = json.load(file)
                file.close()
                file = open(f'/data_files/programs_bak/{file}', 'w')
                json.dump(data, file)
                file.close()
                _gc_collect()
                _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())

    def restore_back_up(self) -> None:
        '''save data set (self.data) from /data_files/back_up.json and program files from /data_files/programs_bak/; called by
        PageSettings._callback_confirm'''
        if not self.load_data_json_file('/data_files/back-up.json'):
            return
        _gc_collect = gc.collect
        _gc_threshold = gc.threshold
        _gc_mem_free = gc.mem_free
        _gc_mem_alloc = gc.mem_alloc
        _gc_collect()
        _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())
        with self.thread_lock:
            files = os.listdir('/data_files/programs')
            for file in files:
                os.remove(f'/data_files/programs/{file}')
            files = os.listdir('/data_files/programs_bak')
            for file in files:
                file = open(f'/data_files/programs_bak/{file}')
                data = json.load(file)
                file.close()
                file = open(f'/data_files/programs/{file}', 'w')
                json.dump(data, file)
                file.close()
                _gc_collect()
                _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())

    def factory_reset(self) -> None:
        '''load data set (self.data) to empty/default initial state; called by self.load_data_json_file and PageSettings._callback_confirm'''
        with self.thread_lock:
            self.data = {'settings': {'midi_thru': False,
                                      'midi_thru_input_port': -1,
                                      'midi_thru_input_channel': -1,
                                      'midi_thru_output_port': -1,
                                      'midi_thru_output_channel': -1,
                                      'midi_learn': False,
                                      'midi_learn_port': -1,
                                      'default_output_velocity': 64},
                         'routing_programs': [],
                         'input_device_mapping': {},
                         'output_device_mapping': {},
                         'input_presets': {},
                         'output_presets': {},
                         'input_devices': {},
                         'output_devices':{}}
            data_file = open(f'/data_files/data.json', 'w')
            json.dump(self.data, data_file)
            data_file.close()
        self.load()

    def load(self) -> None:
        '''load definitions from data set (self.data); called by self.load_data_json_file, router._save and router._save_program'''
        with self.thread_lock:
            programs = self.data['routing_programs']
            self.routing_programs = programs
            self.input_device_mapping = self.data['input_device_mapping']
            self.output_device_mapping = self.data['output_device_mapping']
            self.input_presets = self.data['input_presets']
            self.output_presets = self.data['output_presets']
            self.input_devices = self.data['input_devices']
            self.output_devices = self.data['output_devices']
            self.settings = self.data['settings']
            self.programs_tuple = tuple((program[0] for program in programs))

###### this might not be necessary if the set-up is changed to ID-based data mapping
    def change_in_programs(self, field: str, old_value: str, new_value: str, condition_field: str = '', condition_value: str = '') -> None:
        '''change an old value into a new value for a given field in all program data files; called by router.rename_device and
        router.rename_preset'''
        _gc_collect = gc.collect
        _gc_threshold = gc.threshold
        _gc_mem_free = gc.mem_free
        _gc_mem_alloc = gc.mem_alloc
        _gc_collect()
        _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())
        with self.thread_lock:
            files = os.listdir('/data_files/programs')
            for file in files:
                file = open(f'/data_files/programs/{file}')
                data = json.load(file)
                routing = data['routing']
                if condition_field == '':
                    for route in routing:
                        if route[field] == old_value:
                            route[field] = new_value
                else:
                    for route in routing:
                        if route[field] == old_value and route[condition_field] == condition_value:
                            route[field] = new_value
                file.close()
                file = open(f'/data_files/programs/{file}', 'w')
                json.dump(data, file)
                file.close()
                _gc_collect()
                _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())

    def delete(self) -> None:
        del self.programs_tuple
        del self.routing_programs
        del self.input_device_mapping
        del self.output_device_mapping
        del self.input_presets
        del self.output_presets
        del self.input_devices
        del self.output_devices
        del self.data