''' Main loop fuctions for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

import micropython
import _thread
import machine
import time
import gc
from sys import exit

from router import Router
from ui import UI
from data import Data

_NONE             = const(-1)

_MAIN_LOOP_DELAY  = const(5) # ms

_OVERCLOCK_FREQ   = const(270_000_000)

# global variables to interact with second thread
start_second_thread = False
terminated = False
thread_lock = _thread.allocate_lock()

def init() -> None:
    '''initiations before starting main loops'''
    global ui, router, start_second_thread
    # initiate
    machine.freq(_OVERCLOCK_FREQ)
    gc.enable()
    gc.collect()
    gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    if __debug__: micropython.alloc_emergency_exception_buf(100)
    ui = UI()
    gc.collect()
    gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    _data = Data(ui, thread_lock)
    _data.load_data_json_file()
    gc.collect()
    gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    router = Router(_data, ui, thread_lock)
    ui.link_data_and_router(_data, router)
    gc.collect()
    gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    print('initiate second thread')
    _thread.start_new_thread(second_thread, ())
    # call update to load data
    router.update(already_waiting=True)
    gc.collect()
    gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    print('start second thread')
    with thread_lock:
        start_second_thread = True

def main():
    '''main loop running on fist core, taking care of non time sensitive tasks: ui and processing encoders, user input, midi learn data and
    monitor data'''
    _ticks_diff = time.ticks_diff
    _ticks_ms = time.ticks_ms
######
    # _get_encoder_input = ui._get_encoder_input
    _process_encoder_input = ui.process_encoder_input
    _read_midi_learn_data = router.read_midi_learn_data
    _process_midi_learn_data = ui.process_midi_learn_data
    _process_user_input = ui.process_user_input
    _process_monitor = ui.process_monitor
    _process_program_change_break = router.process_program_change_break
######
    # previous_encoder_input = (None, None)
    previous_midi_learn_data = None
    main_loop_time = time.ticks_ms()
    while True:
        # limit main loop speed to improve stability
        now = _ticks_ms()
        if _ticks_diff(now, main_loop_time) >= _MAIN_LOOP_DELAY:
            main_loop_time = now
            # turn display off after prolonged inactivity
            ui.check_sleep_time_out()
            # process encoders
######
            # encoder_input = _get_encoder_input()
            # if encoder_input != (None, None):
            #     _process_encoder_input(encoder_input)
            _process_encoder_input()
            # process buttons and other input
            _process_user_input()
            # process midi learn input
            midi_learn_data = _read_midi_learn_data()
            if midi_learn_data is not None:
                if midi_learn_data != previous_midi_learn_data:
                    previous_midi_learn_data = midi_learn_data
            if previous_midi_learn_data is not None:
                _process_midi_learn_data(previous_midi_learn_data)
                previous_midi_learn_data = None
            # process router and midi monitor
            _process_monitor()
            # process program change break
            _process_program_change_break()

def second_thread() -> None:
    '''time sensitive loop running on second core, taking care of midi routing'''
    while not start_second_thread:
        time.sleep_ms(100)
    _router = router
    input_ports = _router.midi_ports.input_ports
    note_off_time_tracker = _router.note_off_time_tracker
    _process_timed_note_off_events = _router.process_timed_note_off_events
    routes = _router.routes
    _trigger_note_on = _router.trigger_note_on
    _led = machine.Pin(25, machine.Pin.OUT)
    _led_on = _led.on
    _led_off = _led.off
    _thread_lock = _router.thread_lock
    while not terminated:
        _led_on()
        # check if first thread asks to wait (handshake)
        if _router.request_wait:
            with _thread_lock:
                _router.running = False
                _router.request_wait = False
        while _router.running and not _router.request_wait:
            # quick flash of on-board led (resulting in dim light) to show the second thread is up and running
            _led_on()
            _led_off()
            # process midi input
            for port in input_ports:
                port.process()
            # process timed note off events
            if len(note_off_time_tracker) > 0:
                _process_timed_note_off_events()
            # process trigger button input
            if _router.ui_trigger is not None:
                key = _router.ui_trigger
                with _thread_lock:
                    _router.ui_trigger = None
                for route in routes[key]:
                    note = route['output_note']
                    if note == _NONE:
                        note = route['output_trigger']['note']
                    if note == _NONE:
                        note = 60 # middle C
                    note_off = route['output_note_off']
                    note_off = route['output_trigger']['note_off'] if note_off == _NONE else note_off - 1
                    _trigger_note_on(route['output_port'], route['output_channel'], note, note_off)
    _thread.exit()
    print('second thread terminated successfully')

def shut_down() -> None:
    '''shutting down function'''
    global terminated, ui, router
    with thread_lock:
        terminated = True
        time.sleep_ms(500)
    ui.delete()
    del ui
    router.delete()
    del router
    print('finished shutting down')
    exit()