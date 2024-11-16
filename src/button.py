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
_LONG_PRESS_DELAY       = const(200) # ms

_IRQ_LAST_STATE         = const(0)
_IRQ_IDLE_STATE         = const(1)
_IRQ_LAST_TIME          = const(2)
_IRQ_ONE_BUT_LAST_TIME  = const(3)
_IRQ_AVAILABLE          = const(4)

_BUTTON_EVENT_PRESS      = const(0)
_BUTTON_EVENT_LONG_PRESS = const(1)

class Button():
    '''button handling class; initiated by ui.__init__'''

    def __init__(self, pin_number: int, pull_up: bool = False, long_press: bool = False) -> None:
        self.pin_number = pin_number
        self.long_press = long_press
        self.irq_data = array('l', [_NONE, _NONE, 0, _NONE, 0])
        self.irq_data[_IRQ_IDLE_STATE] = int(pull_up)
        _pin = Pin
        pull_direction = _pin.PULL_UP if pull_up else _pin.PULL_DOWN
        _pin = _pin(pin_number, _pin.IN, pull_direction)
        self.pin = _pin
        _pin.irq(self._callback, _IRQ_RISING_FALLING)

    def close(self) -> None:
        self.pin.irq(handler=None)

    @micropython.viper
    def value(self) -> int:
        '''if long_press == False: return _BUTTON_EVENT_PRESS if pressed; if long_press == True: return _BUTTON_EVENT_PRESS if pressed
        shorter then _LONG_PRESS_DELAY milliseconds or return _BUTTON_EVENT_LONG_PRESS if pressed longer (if kept pressed the trigger
        happens after _LONG_PRESS_DELAY milliseconds); called by ui.process_user_input'''
        irq_data = ptr32(self.irq_data) # type: ignore
        if not irq_data[_IRQ_AVAILABLE]:
            return _NONE
        now = int(time.ticks_ms())
        if int(time.ticks_diff(now, irq_data[_IRQ_LAST_TIME])) < _DEBOUNCE_DELAY:
            return _NONE
        pressed = irq_data[_IRQ_LAST_STATE] != irq_data[_IRQ_IDLE_STATE]
        if bool(self.long_press):
            if pressed:
                difference = int(time.ticks_diff(now, irq_data[_IRQ_LAST_TIME]))
                if difference < _LONG_PRESS_DELAY:
                    return _NONE
                irq_data[_IRQ_AVAILABLE] = 0
                return _BUTTON_EVENT_LONG_PRESS
            difference = int(time.ticks_diff(irq_data[_IRQ_LAST_TIME], irq_data[_IRQ_ONE_BUT_LAST_TIME]))
            irq_data[_IRQ_AVAILABLE] = 0
            return _BUTTON_EVENT_PRESS if difference < _LONG_PRESS_DELAY else _NONE
        irq_data[_IRQ_AVAILABLE] = 0
        return _BUTTON_EVENT_PRESS if pressed else _NONE

    @micropython.viper
    def _callback(self, pin):
        '''callback for pin irq: debounces intput and calls callback function if status changed'''
        irq_data = ptr32(self.irq_data) # type: ignore        
        state = int(pin())
        if state == irq_data[_IRQ_LAST_STATE]:
            return
        irq_data[_IRQ_LAST_STATE] = state
        irq_data[_IRQ_AVAILABLE] = 1
        irq_data[_IRQ_ONE_BUT_LAST_TIME] = irq_data[_IRQ_LAST_TIME]
        irq_data[_IRQ_LAST_TIME] = int(time.ticks_ms())