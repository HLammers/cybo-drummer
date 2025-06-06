''' Library providing data class for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024-2025 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

import os
import json
import gc

import main_loops as ml
from constants import BLANK_LABEL

_NONE         = const(-1)

_NR_IN_PORTS  = const(6)
_MAX_PROGRAMS = const(99)

_ASCII_A      = const(65)

class Data:
    '''overall data class for routing, definitions and settings; initiated once in main_loops.py: init'''

    def __init__(self) -> None:
        self.data = {} # full data set, as stored in json file
        self.trigger_matrix = [[_NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE],
                               [_NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE],
                               [_NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE],
                               [_NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE],
                               [_NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE],
                               [_NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE],
                               [_NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE],
                               [_NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE]],
        self.input_port_mapping = [['', _NONE] for _ in range(_NR_IN_PORTS)]
        self.input_triggers = {}
        self.output_mapping = []
        self.settings = {}
        self.programs = {}

    def load_data_json_file(self, file: str = 'data.json') -> bool:
        '''load data set (self.data) from json file and return True if successful; called by main_loops.py: init and self.restore_back_up'''
        reset = False
        with ml.thread_lock:
            try:
                with open(f'/data_files/{file}') as data_file:
                    self.data = json.load(data_file)
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

    def load_program_json_file(self, bank: int, program: int) -> dict:
        '''return program data_files from json file; called by router.update'''
        return_data = {'program_change': [], 'bank_select': [], 'routing': []}
        try:
            files = os.listdir('/data_files/programs')
        except:
            print('unable to access /data_files/programs')
            return return_data
        for file_name in files:
            if file_name[0] == chr(_ASCII_A + bank) and file_name[1:3] == f'{program:02}':
                try:
                    with open(f'/data_files/programs/{file_name}') as file:
                        return_data = json.load(file)
                except:
                    # print(f'unable to load data file for bank {chr(_ASCII_A + bank)} program {program:02}')
                    pass
                return return_data
        return return_data

    def save_data_json_file(self, file: str = 'data.json') -> None:
        '''save data set (self.data) to json file; called by self.save_back_up, router._save, router.save_program, Page*._save_*_settings
        and Page*.process_user_input'''
        with open(f'/data_files/{file}', 'w') as data_file:
            json.dump(self.data, data_file)

    def save_program_json_file(self, program_data: dict, bank: int, program: int) -> None:
        '''save program data to json file; called by router.save_program'''
        with open(f'/data_files/programs/{chr(_ASCII_A + bank)}{program:02}_{self.programs[bank][program]}.json', 'w') as file:
            with ml.thread_lock:
                json.dump(program_data, file)

    def save_back_up(self) -> None:
        '''save data set (self.data) to /data_files/back_up.json and program files to /data_files/programs_bak/; called by
        PageSettings._callback_confirm'''
        self.save_data_json_file('/data_files/back_up.json')
        _gc = gc
        _gc_collect = _gc.collect
        _gc_threshold = _gc.threshold
        _gc_mem_free = _gc.mem_free
        _gc_mem_alloc = _gc.mem_alloc
        _gc_collect()
        _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())
        with ml.thread_lock:
            try:
                files = os.listdir('/data_files/programs_bak')
            except:
                print('unable to access /data_files/programs_bak')
                return
            for file in files:
                os.remove(f'/data_files/programs_bak/{file}')
            try:
                files = os.listdir('/data_files/programs')
            except:
                print('unable to access /data_files/programs')
                return
            for file_name in files:
                with open(f'/data_files/programs/{file_name}') as file:
                    data = json.load(file)
                with open(f'/data_files/programs_bak/{file_name}', 'w') as file:
                    json.dump(data, file)
                _gc_collect()
                _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())

    def restore_back_up(self) -> None:
        '''save data set (self.data) from /data_files/back_up.json and program files from /data_files/programs_bak/; called by
        PageSettings._callback_confirm'''
        if not self.load_data_json_file('/data_files/back-up.json'):
            return
        _gc = gc
        _gc_collect = _gc.collect
        _gc_threshold = _gc.threshold
        _gc_mem_free = _gc.mem_free
        _gc_mem_alloc = _gc.mem_alloc
        _gc_collect()
        _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())
        with ml.thread_lock:
            try:
                files = os.listdir('/data_files/programs')
            except:
                print('unable to access /data_files/programs')
                return
            for file in files:
                os.remove(f'/data_files/programs/{file}')
            try:
                files = os.listdir('/data_files/programs_bak')
            except:
                print('unable to access /data_files/programs_bak')
                return                
            for file_name in files:
                with open(f'/data_files/programs_bak/{file_name}') as file:
                    data = json.load(file)
                with open(f'/data_files/programs/{file_name}', 'w') as file:
                    json.dump(data, file)
                _gc_collect()
                _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())

    def factory_reset(self) -> None:
        '''load data set (self.data) to empty/default initial state; called by self.load_data_json_file and PageSettings._callback_confirm'''
        with ml.thread_lock:
            self.data = {'settings': {'midi_thru': False,
                                      'midi_thru_input_port': _NONE,
                                      'midi_thru_input_channel': _NONE,
                                      'midi_thru_output_port': _NONE,
                                      'midi_thru_output_channel': _NONE,
                                      'midi_learn': False,
                                      'midi_learn_port': _NONE,
                                      'default_output_velocity': 64},
                         'trigger_matrix': [[_NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE],
                                            [_NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE],
                                            [_NONE, _NONE,    23,    25, _NONE, _NONE, _NONE, _NONE],
                                            [_NONE, _NONE,    21,     3,     4, _NONE,    24, _NONE],
                                            [_NONE, _NONE, _NONE,     2,     0,     5, _NONE, _NONE],
                                            [_NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE],
                                            [_NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE],
                                            [_NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE, _NONE]],
                         'input_port_mapping': [['', _NONE], ['', _NONE], ['', _NONE], ['', _NONE], ['', _NONE], ['', _NONE]],
                         'input_triggers': {},
                         'output_mapping':['', {'channel': 9, 'vel_0_note_off': True, 'running_status': True, 'mapping': []},
                                           '', {'channel': 9, 'vel_0_note_off': True, 'running_status': True, 'mapping': []},
                                           '', {'channel': 9, 'vel_0_note_off': True, 'running_status': True, 'mapping': []},
                                           '', {'channel': 9, 'vel_0_note_off': True, 'running_status': True, 'mapping': []},
                                           '', {'channel': 9, 'vel_0_note_off': True, 'running_status': True, 'mapping': []},
                                           '', {'channel': 9, 'vel_0_note_off': True, 'running_status': True, 'mapping': []}]}
            with open(f'/data_files/data.json', 'w') as file:
                json.dump(self.data, file)
        self.load()

    def load(self) -> None:
        '''load definitions from data set (self.data); called by self.load_data_json_file, router._save and router.save_program'''
        with ml.thread_lock:
            self.settings = self.data['settings']
            self.trigger_matrix = self.data['trigger_matrix']
            self.input_port_mapping = self.data['input_port_mapping']
            self.input_triggers = self.data['input_triggers']
            self.output_mapping = self.data['output_mapping']
            try:
                files = os.listdir('/data_files/programs')
            except:
                print('unable to access /data_files/programs')
                self.programs = {}
                return
            programs = {}
            for file in files:
                try:
                    bank = ord(file[0]) - _ASCII_A
                    program = int(file[1:3])
                except:
                    continue
                if bank in programs:
                    bank_programs = programs[bank]
                else:
                    bank_programs = {}
                    programs[bank] = bank_programs
                bank_programs[program] = file[4:-5]
            self.programs = programs

    def rename_program(self, bank: int, program: int, new_name: str) -> None:
        '''change the program name for a program data file to rename the program; called by router.rename_program'''
        if bank in (programs := self.programs):
            bank_programs = programs[bank]
        else:
            bank_programs = {}
            programs[bank] = bank_programs
        if program in bank_programs:
            old_name = bank_programs[program]
            try:
                prefix = f'/data_files/programs/{chr(_ASCII_A + bank)}{program:02}_'
                os.rename(f'{prefix}{old_name}.json', f'{prefix}{new_name}.json')
            except:
                prefix = f'{chr(_ASCII_A + bank)}{program:02}_'
                print(f'unable to rename {prefix}{old_name}.json to {prefix}{new_name}.json')
        bank_programs[program] = new_name

    def move_program(self, from_bank: int, from_program: int, to_bank: int, to_program: int) -> tuple[int, int]:
        '''change the numbers of all program data files where necessary to change a programs position; called by router.move_program'''
        if from_bank not in (programs := self.programs):
            return from_bank, from_program
        if from_program not in (from_bank_programs := programs[from_bank]):
            return from_bank, from_program
        folder = '/data_files/programs/'
        name = from_bank_programs.pop(from_program)
        if to_bank == from_bank:
            try:
                os.rename(f'{folder}{chr(_ASCII_A + from_bank)}{from_program:02}_{name}.json',
                          f'{folder}{chr(_ASCII_A + to_bank)}{to_program:02}_{name}.temp')
            except:
                print(f'unable to rename {chr(_ASCII_A + from_bank)}{from_program:02}_{name}.json')
            if to_program > from_program:
                self._shift_programs_backward(from_bank, from_program, to_program)
            else:
                self._shift_programs_forward(to_bank, to_program, from_program)
            try:
                os.rename(f'{folder}{chr(_ASCII_A + to_bank)}{to_program:02}_{name}.temp',
                          f'{folder}{chr(_ASCII_A + to_bank)}{to_program:02}_{name}.json')
            except:
                print(f'unable to rename {chr(_ASCII_A + to_bank)}{to_program:02}_{name}.temp')
        else:
            if to_bank in programs:
                to_bank_programs = programs[to_bank]
                if not self._shift_programs_forward(to_bank, to_program):
                    from_bank_programs[from_program] = name
                    return from_bank, from_program
            else:
                to_bank_programs = {}
                programs[to_bank] = to_bank_programs
            to_bank_programs[to_program] = name
            try:
                os.rename(f'{folder}{chr(_ASCII_A + from_bank)}{from_program:02}_{name}.json',
                          f'{folder}{chr(_ASCII_A + to_bank)}{to_program:02}_{name}.json')
            except:
                print(f'unable to rename {chr(_ASCII_A + from_bank)}{from_program:02}_{name}.json')
        return to_bank, to_program

    def delete_program(self, bank: int, program: int, name: str) -> None:
        '''delete program data file or shift programs if the active program is an empty slot; called by router.delete_program'''
        if bank not in (programs := self.programs):
            return
        if program not in programs[bank]:
            self._shift_programs_backward(bank, program)
        else:
            try:
                os.remove(f'/data_files/programs/{chr(_ASCII_A + bank)}{program:02}_{name}.json')
            except:
                print(f'unable to delete {chr(_ASCII_A + bank)}{program:02}_{name}.json')

    def change_in_programs(self, field: str, old_value: str, new_value: str, condition_field: str = '', condition_value = None) -> None:
        '''change an old value into a new value for a given field in all program data files; called by router.rename_voice'''
        _gc = gc
        _gc_collect = _gc.collect
        _gc_threshold = _gc.threshold
        _gc_mem_free = _gc.mem_free
        _gc_mem_alloc = _gc.mem_alloc
        _gc_collect()
        _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())
        with ml.thread_lock:
            try:
                files = os.listdir('/data_files/programs')
            except:
                print('unable to access /data_files/programs')
                return
            for file_name in files:
                with open(f'/data_files/programs/{file_name}') as file:
                    data = json.load(file)
                routing = data['routing']
                changed = False
                if condition_field == '':
                    for route in routing:
                        if route[field] == old_value:
                            route[field] = new_value
                            changed = True
                else:
                    for route in routing:
                        for layer in route['layers'].values():
                            if layer[field] == old_value and layer[condition_field] == condition_value:
                                layer[field] = new_value
                                changed = True
                if changed:
                    with open(f'/data_files/programs/{file_name}', 'w') as file:
                        json.dump(data, file)
                _gc_collect()
                _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())

    def get_program_name(self, bank: int, program: int) -> str:
        '''return program name for program select popup; called by ProgramPopUp.draw'''
        prefix = f'{program:02} '
        try:
            return prefix + ml.data.programs[bank][program]
        except:
            return prefix + BLANK_LABEL

    def delete(self) -> None:
        del self.programs
        del self.trigger_matrix
        del self.input_port_mapping
        del self.input_triggers
        del self.output_mapping
        del self.data

    def _shift_programs_forward(self, bank: int, from_program: int, to_program: int = _NONE) -> bool:
        '''shift all programs from from_program until the first empty slot forward; returns False if failed; called by self.move_program'''
        if bank not in (programs := self.programs):
            return True
        bank_programs = programs[bank]
        if from_program not in bank_programs:
            return True
        if to_program == _NONE:
            n = from_program + 1
            while n in bank_programs:
                n += 1
            if n > _MAX_PROGRAMS:
                return False
        else:
            n = to_program
        prefix = f'/data_files/programs/{chr(_ASCII_A + bank)}'
        for i in range(n, from_program, -1):
            bank_programs[i] = (name := bank_programs.pop(i - 1))
            try:
                os.rename(f'{prefix}{(i - 1):02}_{name}.json', f'{prefix}{i:02}_{name}.json')
            except:
                print(f'unable to shift {chr(_ASCII_A + bank)}{i:02}_{name}.json')
        return True

    def _shift_programs_backward(self, bank: int, from_program: int, to_program: int = _MAX_PROGRAMS) -> None:
        '''shift all programs from from_program plus one one slot backward (deleting existing program on from_program, if any);
        called by self.move_program and self.delete_program'''
        if bank not in (programs := self.programs):
            return
        bank_programs = programs[bank]
        if from_program in bank_programs:
            name = bank_programs[from_program]
            try:
                os.remove(f'/data_files/programs/{chr(_ASCII_A + bank)}{from_program:02}_{name}.json')
            except:
                print(f'unable to delete {chr(_ASCII_A + bank)}{from_program:02}_{name}.json')
        prefix = f'/data_files/programs/{chr(_ASCII_A + bank)}'
        for i in range(from_program, to_program):
            n = i + 1
            if n in bank_programs:
                bank_programs[i] = (name := bank_programs[n])
                try:
                    os.rename(f'{prefix}{n:02}_{name}.json', f'{prefix}{i:02}_{name}.json')
                except:
                    print(f'unable to shift {chr(_ASCII_A + bank)}{n:02}_{name}.json')
            elif i in bank_programs:
                del bank_programs[i]