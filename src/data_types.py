''' Library providing custom data types for Cybo-Drummer - Humanize Those Drum Computers!
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

from math import tanh

_NONE                  = const(-1)

_TRANSIENT_HARD        = const(0)
_TRANSIENT_SMOOTH_1    = const(1)
_TRANSIENT_SMOOTH_2    = const(2)
_TRANSIENT_LINEAR      = const(3)

_COEFFICIENT_COLUMN    = const(0)
_MIN_COLUMN            = const(1)
_MAX_COLUMN            = const(2)

# (coefficient, min value, max value)
_TRANSIENT_DEFINITIONS = (((_NONE, 0, 63), (13, 0, 90), (5.6, 0, 126), (_NONE, 0, 127)),
                          ((_NONE, 64, 127), (13, 37, 127), (5.6, 1, 127), (_NONE, 0, 127)))
_CURVE_COEFFICIENTS    = (0, 0.536, 0.125, 0.0208)

class ChainMapTuple:
    '''tuple-based chain map data type class'''

    def __init__(self, *maps):
        _maps = tuple(maps) if maps else ((),)
        n = 0
        for m in _maps:
            n += len(m)
        self._maps = _maps
        self._len = n

    def __getitem__(self, i):
        for m in self._maps:
            n = len(m)
            if i < n:
                return m[i]
            i -= n
        raise StopIteration

    def __iter__(self):
        for i in range(self._len):
            yield self.__getitem__(i)

    def __len__(self):
        return self._len

    def index(self, v):
        k = 0
        for m in self._maps:
            for vv in m:
                if v == vv:
                    return k
                k += 1
        raise KeyError(v)

class GenOptions:
    '''options generator'''

    def __init__(self, length: int, offset: int = 0, first_options: tuple = (), additional_options: tuple = (), func = None,
                 argument = None, suffix: str = ''):
        self._len = length
        offset -= len(first_options)
        self._offset = offset
        self._first_options = first_options
        self._additional_options = additional_options
        self._func = func
        self.argument = argument
        self.suffix = suffix

    def __getitem__(self, i):
        l = self._len
        if i >= l:
            raise StopIteration
        if i < len(first_options := self._first_options):
            return first_options[i]
        n = len(additional_options := self._additional_options)
        if i >= l - n:
            return additional_options[i + n - l]
        i += self._offset
        _func = self._func
        argument = self.argument
        if _func is None:
            ret = i
        elif argument is None:
            ret = _func(i)
        else:
            ret = _func(i, argument)
        if (suffix := self.suffix) != '':
            ret = f'{ret}{suffix}'
        return ret

    def __iter__(self):
        for i in range(self._len):
            yield self.__getitem__(i)

    def __len__(self):
        return self._len

class GenCurves():
    '''curve/transition generator based on hyperboles / hyperbolic tangent sigmoid functions'''

    def __init__(self, min_value: int, max_value: int, curve: int, threshold: int, transient: int, layer: int, scale: bool):
        self.min_value = min_value
        self.max_value = max_value
        self.curve = curve
        self.threshold = threshold
        self.transient = transient
        self.layer = layer
        self.scale = scale
        definition = _TRANSIENT_DEFINITIONS[self.layer][self.transient]
        self._definition = definition
        self._transient_step = 127 / ((max_v := definition[_MAX_COLUMN]) - (min_v := definition[_MIN_COLUMN]))
        self._transient_min_value = min_v
        self._transient_max_value = max_v
        if curve == 0:
            self._curve_step = (max_value - min_value) / 127
            return
        self._a = 127 * (a := _CURVE_COEFFICIENTS[abs(curve)])
        if curve > 0:
            self._curve_step = (max_value - min_value) / 127
        else:
            self._d = max_value - min_value
            self._b = a / (1 + a)
            self._c = 1 + a

    def __getitem__(self, i: int, recursive: bool=False) -> int:
        if i < self.threshold:
            return 0
        scale = self.scale
        if (transient := self.transient) != _NONE and scale:
            if i < (min_value := self._transient_min_value) or i > self._transient_max_value:
                return 0
            else:
                j = (i - min_value) * self._transient_step
        else:
            j = i
        if (curve := self.curve) == 0:
            value = self.min_value + self._curve_step * j
        elif curve > 0:
            value = self.min_value + self._curve_step * ((a := self._a) * j + 127 * j) / (j + a)
        else:
            value = self.min_value + self._d * (-(a := self._a) / (j - 127 - a) - self._b) * self._c
        if transient == _NONE:
            return int(value + 0.5)        
        definition = self._definition
        if transient == _TRANSIENT_LINEAR:
            t = i / 127
        elif transient == _TRANSIENT_HARD:
            t = 0 if i < 64 else 1
        else:
            t = 0.5 * tanh(definition[_COEFFICIENT_COLUMN]*(i - 63.5)/127) + 0.5
        if self.layer == 0:
            t = 1 - t
        if recursive or not scale:
            return int(t * value + 0.5)
        max_value = 0
        for k in range(128):
            if (y:= self.__getitem__(k, True)) > max_value:
                max_value = y
        if max_value == 0:
            return int(t * value + 0.5)
        return int(t * 127 / max_value * value + 0.5)

    def __iter__(self):
        for i in range(128):
            yield self.__getitem__(i)

    def __len__(self):
        return 128