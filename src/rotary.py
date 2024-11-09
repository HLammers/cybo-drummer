''' Rotary encoder library for Cybo-Drummer - Humanize Those Drum Computers!
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
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    
    This code builds upon code fragments and ideas taken from:
        encoder_portable, copyright (c) 2017-2022 Peter Hinch, https://github.com/peterhinch/micropython-samples/tree/master/encoders
        encoder_timed, copyright (c) 2016-2021 Peter Hinch, https://github.com/peterhinch/micropython-samples/tree/master/encoders
    Acceleration algorithm taken from Adaptive User Input with a Rotary Encoder, marco_c, 20 April 2026, updated on 30 May 2017,
    https://arduinoplusplus.wordpress.com/2016/04/20/adaptive-user-input-with-a-rotary-encoder/'''

import micropython
from machine import Pin, disable_irq, enable_irq
import time
from array import array

_NONE                        = const(-1)

_IRQ_RISING_FALLING          = const(12) # Pin.IRQ_RISING | Pin.IRQ_FALLING

_RANGE_DIVIDER               = const(80)
_RATE_DIVIDER                = const(10)
_MAX_RATE                    = const(50)

_PROCESS_DELAY               = const(300) # ms
_RESET_TIME                  = const(100) # ms

_IRQ_CHANGED                 = const(0)
_IRQ_COUNT                   = const(1)
_IRQ_POS                     = const(2)
_IRQ_LAST_INPUT_TIME         = const(3)
_IRQ_ONE_BUT_LAST_INPUT_TIME = const(4)
_IRQ_LAST_PULSE_TIME         = const(5)
_IRQ_VALUE_A                 = const(6)
_IRQ_VALUE_B                 = const(7)

class Rotary():
    '''rotary encoder handling class; initiated by ui.__init__'''

    def __init__(self, pin_num_a: int, pin_num_b: int, min_val: int = 0, max_val: int = 10, pull_up: bool = False) -> None:
        self.min_val = min_val
        self.max_val = max_val
        self.irq_data = array('l', [0, 0, 0, _NONE, _NONE, _NONE, 0, 0])
        self.irq_data[_IRQ_POS] = min_val
        self.previous_pos = min_val
        self.last_process_time = _NONE
        range = max_val - min_val + 1
        self.range = range
        self.multiplier = range // _RANGE_DIVIDER
        if pull_up:
            _pin_a = Pin(pin_num_a, Pin.IN, Pin.PULL_UP)
            _pin_b = Pin(pin_num_b, Pin.IN, Pin.PULL_UP)
        else:
            _pin_a = Pin(pin_num_a, Pin.IN)
            _pin_b = Pin(pin_num_b, Pin.IN)
        self._pin_a = _pin_a
        self._pin_b = _pin_b
        self.irq_data[_IRQ_VALUE_A] = _pin_a()
        self.irq_data[_IRQ_VALUE_B] = _pin_b()
        _pin_a.irq(self._callback_a, _IRQ_RISING_FALLING, hard=True)
        _pin_b.irq(self._callback_b, _IRQ_RISING_FALLING, hard=True)

    def set(self, value: int|None = None, min_val: int|None = None, max_val: int|None = None) -> None:
        '''sets rotary encoder value, range and increment; called by block .update functions, TextEdit.open, *PopUp.draw,
        Page._sub_page_selector and Page._initiate_encoder'''
        if value is not None:
            state = disable_irq()
            self.irq_data[_IRQ_POS] = value
            enable_irq(state)
            self.previous_pos = value
        if min_val is not None:
            self.min_val = min_val
        if max_val is not None:
            self.max_val = max_val
            if min_val is not None:
                range = max_val - min_val + 1
                self.range = range
                self.multiplier = range // _RANGE_DIVIDER

    @micropython.viper
    def value(self) -> int:
        '''return current encoder value if a new (changed) value is available and reset self.changed; return _NONE if no new (changed)
        value is available; called by ui.get_encoder_input'''
        irq_data = ptr32(self.irq_data) # type: ignore
        current_time = int(time.ticks_ms())
        if not irq_data[_IRQ_CHANGED]:
            state = disable_irq()
            last_time = irq_data[_IRQ_LAST_PULSE_TIME]
            count = irq_data[_IRQ_COUNT]
            enable_irq(state)
            if last_time != _NONE and count > 0 and int(time.ticks_diff(current_time, last_time)) > _RESET_TIME:
                state = disable_irq()
                irq_data[_IRQ_COUNT] = 0
                enable_irq(state)
            return _NONE
        last_time = int(self.last_process_time)
        if last_time != _NONE and int(time.ticks_diff(current_time, last_time)) < _PROCESS_DELAY:
            return _NONE
        self.last_process_time = current_time
        state = disable_irq()
        irq_data[_IRQ_CHANGED] = 0
        enable_irq(state)
        min_val = int(self.min_val)
        max_val = int(self.max_val)
        range = int(self.range)
        if min_val >= max_val:
            state = disable_irq()
            irq_data[_IRQ_POS] = min_val
            enable_irq(state)
            return min_val
        previous_pos = int(self.previous_pos)
        state = disable_irq()
        pos = int(irq_data[_IRQ_POS])
        enable_irq(state)
        delta = pos - previous_pos
        pos = previous_pos + int(self._step()) * delta
        if pos < min_val:
            pos = pos + range * ((min_val - pos) // range + 1)
        elif pos > max_val:
            pos = min_val + (pos - min_val) % range
        state = disable_irq()
        irq_data[_IRQ_POS] = pos
        enable_irq(state)
        self.previous_pos = pos
        return pos

    @micropython.viper
    def _step(self) -> int:
        '''return step size dependent on rotation speed; called by self.value'''
        irq_data = ptr32(self.irq_data) # type: ignore
        state = disable_irq()
        last_time = irq_data[_IRQ_LAST_INPUT_TIME]
        one_but_last_time = irq_data[_IRQ_ONE_BUT_LAST_INPUT_TIME]
        enable_irq(state)
        delta = int(time.ticks_diff(last_time, one_but_last_time))
        if delta == 0:
            return 1
        multiplier = int(self.multiplier)
        rate = int(min(_MAX_RATE, 1000 // delta))
        return 1 + multiplier * (1 << (rate // _RATE_DIVIDER)) - multiplier

    def close(self) -> None:
        self._pin_a.irq(None, 0)
        self._pin_b.irq(None, 0)

    @micropython.viper
    def _callback_a(self, pin):
        '''callback for rotary a pin irq; called (assigned) by self.__init__'''
        irq_data = ptr32(self.irq_data) # type: ignore
        if (value := int(pin())) == irq_data[_IRQ_VALUE_A]: # reject short pulses
            return
        irq_data[_IRQ_VALUE_A] = value
        forward = value ^ int(self._pin_b()) ^ 1
        now = int(time.ticks_ms())
        irq_data[_IRQ_LAST_PULSE_TIME] = now
        count = irq_data[_IRQ_COUNT]
        if count < 3:
            irq_data[_IRQ_COUNT] = count + 1
            return
        state = disable_irq()
        irq_data[_IRQ_COUNT] = 0
        irq_data[_IRQ_POS] = irq_data[_IRQ_POS] + 1 if forward else irq_data[_IRQ_POS] - 1
        irq_data[_IRQ_ONE_BUT_LAST_INPUT_TIME] = irq_data[_IRQ_LAST_INPUT_TIME]
        irq_data[_IRQ_LAST_INPUT_TIME] = now
        irq_data[_IRQ_CHANGED] = 1
        enable_irq(state)

    @micropython.viper
    def _callback_b(self, pin):
        '''callback for rotary b pin irq; called (assigned) by self.__init__'''
        irq_data = ptr32(self.irq_data) # type: ignore
        if (value := int(pin())) == irq_data[_IRQ_VALUE_B]: # reject short pulses
            return
        irq_data[_IRQ_VALUE_B] = value
        forward = value ^ int(self._pin_a())
        now = int(time.ticks_ms())
        irq_data[_IRQ_LAST_PULSE_TIME] = now
        count = irq_data[_IRQ_COUNT]
        if count < 3:
            irq_data[_IRQ_COUNT] = count + 1
            return
        state = disable_irq()
        irq_data[_IRQ_COUNT] = 0
        irq_data[_IRQ_POS] = irq_data[_IRQ_POS] + 1 if forward else irq_data[_IRQ_POS] - 1
        irq_data[_IRQ_ONE_BUT_LAST_INPUT_TIME] = irq_data[_IRQ_LAST_INPUT_TIME]
        irq_data[_IRQ_LAST_INPUT_TIME] = now
        irq_data[_IRQ_CHANGED] = 1
        enable_irq(state)