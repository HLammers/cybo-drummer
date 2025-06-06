''' Main loop fuctions for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024-2025 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

_PULSE = False

import micropython
import _thread
import machine
import time
import gc
from sys import exit

# global variables to store thread lock, ui instance, data instance and router instance
thread_lock = _thread.allocate_lock()
ui = None
data = None
router = None

from router import Router
import ui as ui_lib
from data import Data

_NONE                = const(-1)

_MAIN_LOOP_DELAY     = const(100) # ms
_SECOND_THREAD_DELAY = const(1000) # ms
_PULSE_DELAY         = const(5000) # ms

_OVERCLOCK_FREQ      = const(300_000_000) # Hz

def init() -> None:
    '''initiations before starting main loops'''
    global ui, data, router
    # initiate
    machine.freq(_OVERCLOCK_FREQ)
    _gc = gc
    _gc_collect = _gc.collect
    _gc_threshold = _gc.threshold
    _gc_mem_free = _gc.mem_free
    _gc_mem_alloc = _gc.mem_alloc
    _gc.enable()
    _gc_collect()
    _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())
    if __debug__: micropython.alloc_emergency_exception_buf(100)
    ui = ui_lib.UI()
    _gc_collect()
    _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())
    data = Data()
    data.load_data_json_file()
    _gc_collect()
    _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())
    router = Router()
    _gc_collect()
    _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())
    _thread.start_new_thread(second_thread, ())
    # call update to load data
    router.update(already_waiting=True)
    _gc_collect()
    _gc_threshold(_gc_mem_free() // 4 + _gc_mem_alloc())
    # draw screen
    ui.display.draw_screen()
    with thread_lock:
        router.start_second_thread = True

def main():
    '''main loop running on fist core, taking care of non time sensitive tasks: ui and processing encoders, user input, midi learn data and
    monitor data'''
    _process_encoder_input = ui.process_encoder_input # type: ignore
    _process_user_input = ui.process_user_input # type: ignore
    _read_midi_learn_data = router.read_midi_learn_data # type: ignore
    _process_midi_learn_data = ui.process_midi_learn_data # type: ignore
    _process_monitor = ui.process_monitor # type: ignore
    _process_program_change_break = router.process_program_change_break # type: ignore
    _draw_screen = ui.display.draw_screen # type: ignore
    previous_midi_learn_data = None
    _time = time
    _ticks_ms = _time.ticks_ms
    _ticks_diff = _time.ticks_diff
    _sleep_ms = _time.sleep_ms
    if _PULSE:
        last_pulse = _ticks_ms()
    last_loop = _ticks_ms()
    while True:
        _sleep_ms(_MAIN_LOOP_DELAY)
        last_loop = _ticks_ms()
        if _PULSE and _ticks_diff(last_loop, last_pulse) > _PULSE_DELAY:
            print('main thread pulse')
            last_pulse = last_loop
        # limit main loop speed to improve stability
        time.sleep_ms(_MAIN_LOOP_DELAY)
        ui.check_sleep_time_out() # type: ignore
        # process encoders
        redraw = _process_encoder_input()
        # process buttons and other input
        redraw |= _process_user_input()
        # process midi learn input
        if (midi_learn_data := _read_midi_learn_data()) is not None:
            if midi_learn_data != previous_midi_learn_data:
                previous_midi_learn_data = midi_learn_data
        if previous_midi_learn_data is not None:
            redraw |= _process_midi_learn_data(previous_midi_learn_data)
            previous_midi_learn_data = None
        # process router and midi monitor
        redraw |= _process_monitor()
        # process program change break
        _process_program_change_break()
        if redraw:
            _draw_screen()

def second_thread() -> None:
    '''time sensitive loop running on second core, taking care of midi routing'''
    print('second thread: wait')
    _router = router
    while _router is None:
        pass
    while _router.start_second_thread:
        pass
    print('second thread: initiate')
    input_ports = _router.midi_ports.input_ports # type: ignore
    _process_timed_note_off_events = _router.process_timed_note_off_events # type: ignore
    routes = _router.routes # type: ignore
    _trigger_note_on = _router.trigger_note_on # type: ignore
    _led = machine.Pin(25, machine.Pin.OUT)
    _led_on = _led.on
    _led_off = _led.off
    _thread_lock = thread_lock
    print('second thread: start')
    _time = time
    _ticks_ms = _time.ticks_ms
    _ticks_diff = _time.ticks_diff
    _time.sleep_ms(_SECOND_THREAD_DELAY)
    while not _router.terminated:
        _led_on()
        # check if first thread asks to wait (handshake)
        if _router.request_wait: # type: ignore
            _led_off()
            with _thread_lock:
                _router.running = False # type: ignore
                _router.request_wait = False # type: ignore
        if _PULSE:
            last_pulse = _ticks_ms()
        while _router.running and not _router.request_wait: # type: ignore
            if _PULSE and _ticks_diff(_ticks_ms(), last_pulse) > _PULSE_DELAY:
                print('second thread pulse')
                last_pulse = _ticks_ms()
            _led_on()
            # process midi input
            for port in input_ports:
                port.process()
            # process timed note off events
            _process_timed_note_off_events()
            # process trigger button input
            if (trigger := _router.ui_trigger) is not None: # type: ignore
                with _thread_lock:
                    _router.ui_trigger = None # type: ignore
                for route in routes[trigger]:
                    if (note := route['output_note']) == _NONE:
                        note = 60 # middle C
                    note_off = route['note_off']
                    _trigger_note_on(route['output_port'], route['output_channel'], note, note_off)
        _led_off()
    _thread.exit()
    print('second thread: terminated')

def shut_down() -> None:
    '''shutting down function'''
    global ui, router
    with thread_lock:
        router.terminated = True # type: ignore
        now = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), now) < 500:
            pass
    ui.delete() # type: ignore
    data.delete() # type: ignore
    del ui
    router.delete() # type: ignore
    del router
    print('finished shutting down')
    exit()