''' Library providing custom data types for Cybo-Drummer - Humanize Those Drum Computers!
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

_A = (0, 0.536, 0.125, 0.0208)

class ChainMapTuple:
    '''tuple-based chain map data type class'''

    def __init__(self, *maps):
        if maps:
            self._maps = tuple(maps)
        else:
            self._maps = ((),)
        self._len = 0
        for m in self._maps:
            self._len += len(m)

    def __getitem__(self, i):
        for m in self._maps:
            if i < len(m):
                return m[i]
            i -= len(m)
        raise StopIteration

    def __iter__(self):
        for i in range(self._len):
            item = self.__getitem__(i)
            yield item

    def __len__(self):
        return self._len

    def __repr__(self):
        return f'({', '.join([repr(m)[1:-1] if len(m) > 1 else repr(m)[1:-2] for m in self._maps])})'

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

    def __init__(self, length: int, offset: int = 0, first_options: tuple = (), func = None, suffix: str = ''):
        if offset is not None:
            length += 1
        self._len = length
        offset -= len(first_options)
        self._offset = offset
        self._first_options = first_options
        self._func = func
        self.suffix = ''

    def __getitem__(self, i):
        if i >= self._len:
            raise StopIteration
        first_options = self._first_options
        if i < len(first_options):
            return first_options[i]
        i += self._offset
        _func = self._func
        suffix = self.suffix
        ret = i if _func is None else _func(i)
        if suffix != '':
            ret = f'{ret}{suffix}'
        return ret

    def __iter__(self):
        for i in range(self._len):
            item = self.__getitem__(i)
            yield item

    def __len__(self):
        return self._len

    def __repr__(self):
        return f'({', '.join(["'" + str(self.__getitem__(i)) + "'" for i in range(self._len)])})'

class GenCurves():
    '''curve generator based on hyperboles'''

    def __init__(self, min_value: int, max_value: int, curve: int):
        self.min_value = min_value
        self.max_value = max_value
        self.curve = curve
        a = _A[abs(curve)]
        if curve == 0:
            self._step = (max_value - min_value) / 127
            return
        self._a = 127 * a
        if curve > 0:
            self._step = (max_value - min_value) / 127
        else:
            self._d = max_value - min_value
            self._b = a / (1 + a)
            self._c = 1 + a

    def __getitem__(self, i: int) -> int:
        curve = self.curve
        if curve == 0:
            value = self.min_value + self._step * i
        elif curve > 0:
            a = self._a
            value = self.min_value + self._step * (a * i + 127 * i) / (i + a)
        else:
            a = self._a
            value = self.min_value + self._d * (-a / (i - 127 - a) - self._b) * self._c
        return int(value + 0.5)

    def __iter__(self):
        for i in range(128):
            item = self.__getitem__(i)
            yield item

    def __len__(self):
        return 128

    def __repr__(self):
        return f'({', '.join([str(self.__getitem__(i)) for i in range(128)])})'