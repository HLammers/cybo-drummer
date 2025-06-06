''' Rotary encoder library for Cybo-Drummer - Humanize Those Drum Computers!
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
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    
    This code builds upon code fragments and ideas taken from:
        encoder_portable, copyright (c) 2017-2022 Peter Hinch, https://github.com/peterhinch/micropython-samples/tree/master/encoders
        encoder_timed, copyright (c) 2016-2021 Peter Hinch, https://github.com/peterhinch/micropython-samples/tree/master/encoders
        encoder.py asynchronous driver for incremental quadrature encoder, copyright (c) 2021-2024 Peter Hinch,
            https://github.com/peterhinch/micropython-async/blob/master/v3/primitives/encoder.py
    Acceleration algorithm taken from Adaptive User Input with a Rotary Encoder, marco_c, 20 April 2016, updated on 30 May 2017,
    https://arduinoplusplus.wordpress.com/2016/04/20/adaptive-user-input-with-a-rotary-encoder/'''

import micropython
from machine import Pin
import time
import math

_NONE               = const(-1)

_RANGE_DIVIDER      = const(80)
_RATE_DIVIDER       = const(10)
_MAX_RATE           = const(50)

_IRQ_RISING_FALLING = const(12) # Pin.IRQ_RISING | Pin.IRQ_FALLING

_RESET_DELAY        = const(10) # ms
_PROCESS_DELAY      = const(150) # ms

class Encoder:
    '''rotary encoder handling class; initiated by ui.__init__'''

    def __init__(self, pin_num_a, pin_num_b, value=0, div=1, max_val=_NONE):
        self.div = div
        self.max_val = max_val
        self.val = value * div
        self.multiplier = (max_val + 1) // _RANGE_DIVIDER
        ###### add Pin.PULL_UP if the rotary encoders have not external pull up resisters
        # self._pin_a = (_pin_a := Pin(pin_num_a, Pin.IN, Pin.PULL_UP))
        # self._pin_b = (_pin_b := Pin(pin_num_b, Pin.IN, Pin.PULL_UP))
        self._pin_a = (_pin_a := Pin(pin_num_a, Pin.IN))
        self._pin_b = (_pin_b := Pin(pin_num_b, Pin.IN))
        self.a = _pin_a()
        self.b = _pin_b()
        self.prev_val = _NONE
        self.prev_div_val = value
        self.out_val = value
        self.prev_out_val = value
        self.last_time = _NONE
        self.previous_time = _NONE
        self.last_value_out = _NONE
        _pin_a.irq(trigger=_IRQ_RISING_FALLING, handler=self._callback_a)
        _pin_b.irq(trigger=_IRQ_RISING_FALLING, handler=self._callback_b)

    def set(self, value: int, max_val: int = _NONE) -> None:
        '''sets rotary encoder value, range and increment; called by block .update functions, SelectBlock.set_options, TextEdit.open,
        *PopUp.draw, TriggerPopUp._update, ChordPopUp.open, Page._sub_page_selector and Page._initiate_nav_encoder'''
        self.val = value * self.div
        self.prev_val = _NONE
        self.prev_div_val = value
        self.out_val = value
        self.prev_out_val = value
        self.last_time = _NONE
        self.previous_time = _NONE
        self.last_value_out = _NONE
        if max_val != _NONE:
            self.max_val = max_val
            self.multiplier = (max_val + 1) // _RANGE_DIVIDER

    def value(self) -> int:
        '''return current encoder value if a new value is available, otherwise return _NONE; called by ui.process_encoder_input'''
        _time = time
        max_val = self.max_val
        if (val := self.val) == (prev_val := self.prev_val) or max_val == _NONE:
            if _time.ticks_diff(_time.ticks_ms(), self.last_value_out) > _RESET_DELAY:
                self.val = (val := self.prev_div_val * self.div)
                self.prev_val = val
            return _NONE
        prev_val = self.prev_val
        self.prev_val = val
        self.previous_time = (last_time := self.last_time)
        self.last_time = (current_time := _time.ticks_ms())
        if last_time == _NONE or _time.ticks_diff(current_time, last_time) < _PROCESS_DELAY:
            return _NONE
        div_val = math.ceil(val / self.div) if val > prev_val else math.floor(val / self.div)
        if not (d_val := div_val - self.prev_div_val):
            return _NONE
        self.prev_div_val = div_val
        out_val = self.out_val + (step := self._step() * d_val)
        if abs(step) == 1:
            out_val %= max_val + 1
        else:
            out_val = max(min(out_val, max_val), 0)
        if out_val == self.prev_out_val:
            return _NONE
        self.out_val = out_val
        self.prev_out_val = out_val
        self.last_value_out = current_time
        return out_val

    def close(self) -> None:
        self._pin_a.irq(None, 0)
        self._pin_b.irq(None, 0)
        
    def _callback_a(self, pin_a):
        '''callback for rotary a pin irq; called (assigned) by self.__init__'''
        if (a := int(pin_a())) == int(self.a):
            return
        self.a = a
        self.val -= 1 if a ^ self._pin_b() else -1

    def _callback_b(self, pin_b):
        '''callback for rotary b pin irq; called (assigned) by self.__init__'''
        if (b := pin_b()) == self.b:
            return
        self.b = b
        self.val += 1 if b ^ self._pin_a() else -1

    @micropython.viper
    def _step(self) -> int:
        '''return step size dependent on rotation speed; called by self.value'''
        if (delta := int(time.ticks_diff(self.last_time, self.previous_time))) == 0:
            return 1
        multiplier = int(self.multiplier)
        return 1 + multiplier * (1 << (int(min(_MAX_RATE, 1000 // delta)) // _RATE_DIVIDER)) - multiplier