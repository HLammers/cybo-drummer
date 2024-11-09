''' Button library for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024 Harm Lammers

    MIT licence:

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to
    the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
    CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'''

import micropython
from machine import Pin
import time
from array import array

_NONE                   = const(-1)

_IRQ_RISING_FALLING     = Pin.IRQ_RISING | Pin.IRQ_FALLING

_DEBOUNCE_DELAY         = const(50) # ms
_KEPT_PRESSED_DELAY     = const(200) # ms

_IRQ_LAST_STATE         = const(0)
_IRQ_IDLE_STATE         = const(1)
_IRQ_LAST_TIME          = const(2)
_IRQ_AVAILABLE          = const(3)

_BUTTON_EVENT_RELEASED  = const(0)
_BUTTON_EVENT_PRESSED   = const(1)
_BUTTON_EVENT_KEPT      = const(2)

class Button():
    '''button handling class; initiated by ui.__init__'''

    def __init__(self, pin_number: int, pull_up: bool = False, trigger_kept_pressed: bool = False) -> None:
        self.pin_number = pin_number
        self.trigger_kept_pressed = trigger_kept_pressed
        self.irq_data = array('l', [_NONE, _NONE, 0, 0])
        self.irq_data[_IRQ_IDLE_STATE] = int(pull_up)
        _pin = Pin
        pull_direction = _pin.PULL_UP if pull_up else _pin.PULL_DOWN
        _pin = _pin(pin_number, _pin.IN, pull_direction)
        self.pin = _pin
        self.last_pressed_time = _NONE
        _pin.irq(self._callback, _IRQ_RISING_FALLING)

    def close(self) -> None:
        self.pin.irq(handler=None)

    @micropython.viper
    def value(self) -> int:
        '''return 1 if triggered and trigger_kept_pressed == False, 1 if short pressed and trigger_kept_pressed == True, 2 if
        kept pressed and trigger_kept_pressed == True, 0 if released and trigger_kept_ressed == True or _NONE if no new data is
        available (yet); called by ui.process_user_input'''
        irq_data = ptr32(self.irq_data) # type: ignore
        if not irq_data[_IRQ_AVAILABLE]:
            return _NONE
        now = int(time.ticks_ms())
        if int(time.ticks_diff(now, irq_data[_IRQ_LAST_TIME])) < _DEBOUNCE_DELAY:
            return _NONE
        pressed = irq_data[_IRQ_LAST_STATE] != irq_data[_IRQ_IDLE_STATE]
        if bool(self.trigger_kept_pressed):
            if pressed:
                if int(self.last_pressed_time) == _NONE:
                    self.last_pressed_time = irq_data[_IRQ_LAST_TIME]
                difference = int(time.ticks_diff(now, int(self.last_pressed_time)))
                if difference < _KEPT_PRESSED_DELAY:
                    return _NONE
                irq_data[_IRQ_AVAILABLE] = 0
                return _BUTTON_EVENT_KEPT
            difference = int(time.ticks_diff(irq_data[_IRQ_LAST_TIME], int(self.last_pressed_time)))
            self.last_pressed_time = _NONE
            irq_data[_IRQ_AVAILABLE] = 0
            return _BUTTON_EVENT_PRESSED if difference < _KEPT_PRESSED_DELAY else _BUTTON_EVENT_RELEASED
        irq_data[_IRQ_AVAILABLE] = 0
        return _BUTTON_EVENT_PRESSED if pressed else _NONE

    @micropython.viper
    def _callback(self, pin):
        '''callback for pin irq: debounces intput and calls callback function if status changed'''
        irq_data = ptr32(self.irq_data) # type: ignore        
        state = int(pin())
        if state == irq_data[_IRQ_LAST_STATE]:
            return
        irq_data[_IRQ_LAST_STATE] = state
        irq_data[_IRQ_AVAILABLE] = 1
        irq_data[_IRQ_LAST_TIME] = int(time.ticks_ms())