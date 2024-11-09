''' MIDI tools library for Cybo-Drummer - Humanize Those Drum Computers!
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

_NOTES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
    
@micropython.viper
def number_to_note(number: int):
    '''convert a note number to a note name; called by ui.process_monitor, page_input constant definitions and page_output constant
    definitions'''
    if 0 <= number <= 127:
        octave = number // 12 - 1
        note = _NOTES[number % 12]
        return f'{note}{octave}'

# def note_to_number(note: str):
#     '''convert a note name to a note number; not called anywhere'''
#     if note[1] == '#':
#         base_note = note[:2]
#         octave = note[2:]
#     else:
#         base_note = note[:1]
#         octave = note[1:]
#     try:
#         octave = int(octave) + 1
#     except:
#         return
#     if base_note in _NOTES:
#         number = 12 * octave + _NOTES.index(base_note)
#         if 0 <= number <= 127:
#             return number