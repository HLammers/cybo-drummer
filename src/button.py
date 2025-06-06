''' Button library for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024-2025 Harm Lammers

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

from machine import Pin
import time

_IRQ_RISING_FALLING      = const(12) # Pin.IRQ_RISING | Pin.IRQ_FALLING

_IDLE_STATE              = const(1)

_DEBOUNCE_DELAY          = const(50) # ms
_LONG_PRESS_DELAY        = const(500) # ms

_BUTTON_EVENT_NONE       = const(0) # use 0 as NONE so button.value can be interpreted as bool
_BUTTON_EVENT_PRESS      = const(1)
_BUTTON_EVENT_LONG_PRESS = const(2)

class Button():
    '''button handling class; initiated by ui.__init__'''

    def __init__(self, pin_number: int, long_press: bool = False) -> None:
        self.pin_number = pin_number
        self.long_press = long_press
        self.state = _IDLE_STATE
        self.prev_state = _IDLE_STATE
        self.last_time = _IDLE_STATE
        self.prev_time = time.ticks_ms()
        self.pin = (_pin := Pin(pin_number, Pin.IN, Pin.PULL_UP))
        _pin.irq(self._callback, _IRQ_RISING_FALLING)

    def close(self) -> None:
        self.pin.irq(handler=None)

    def value(self) -> int:
        '''if long_press == False: return _BUTTON_EVENT_PRESS if pressed; if long_press == True: return _BUTTON_EVENT_PRESS if pressed
        shorter then _LONG_PRESS_DELAY milliseconds or return _BUTTON_EVENT_LONG_PRESS if pressed longer (if kept pressed the trigger
        happens after _LONG_PRESS_DELAY milliseconds); called by ui.process_user_input'''
        if (state := self.state) == self.prev_state:
            return _BUTTON_EVENT_NONE
        self.prev_state = state
        self.prev_time = (prev_time := self.last_time)
        self.last_time = (current_time := time.ticks_ms())
        if time.ticks_diff(current_time, prev_time) < _DEBOUNCE_DELAY:
            return _BUTTON_EVENT_NONE
        released = state == _IDLE_STATE
        if self.long_press:
            if released:
                delta = time.ticks_diff(current_time, prev_time)
                return _BUTTON_EVENT_LONG_PRESS if delta > _LONG_PRESS_DELAY else _BUTTON_EVENT_PRESS
            return _BUTTON_EVENT_NONE
        return _BUTTON_EVENT_NONE if released else _BUTTON_EVENT_PRESS

    def _callback(self, pin):
        '''callback for pin irq: stores state'''
        self.state = pin()