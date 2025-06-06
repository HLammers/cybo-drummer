''' MIDI tools library for Cybo-Drummer - Humanize Those Drum Computers!
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

import micropython

from constants import NOTES

_NONE        = const(-1)
_OCTAVE_NONE = const(-2)

@micropython.viper
def number_to_note(number: int):
    '''convert a note number to a note name; called by ui.process_monitor, page_input constant definitions and page_output constant
    definitions'''
    return f'{NOTES[number % 12]}{number // 12 - 1}' if 0 <= number <= 127 else ''

@micropython.viper
def number_to_base_note(number: int) -> int:
    '''convert a note number to its base note number; called by PageTools.process_user_input, PageTools.midi_learn,
    PageTools._initiate_multipad, PageTools._identify_toms_parameters, PageTools.identify_multi_parameters, PageTools._set_base_note
    and PageTools._set_multi_key'''
    return number % 12 if 0 <= number <= 127 else _NONE

@micropython.viper
def number_to_octave(number: int) -> int:
    '''convert a note number to its octave number; called by PageTools.process_user_input, PageTools.midi_learn,
    PageTools._initiate_multipad, PageTools._identify_toms_parameters, PageTools.identify_multi_parameters, PageTools._set_base_note
    and PageTools._set_multi_key'''
    return number // 12 - 1 if 0 <= number <= 127 else _OCTAVE_NONE

@micropython.viper
def note_from_number_and_octave(note: int, octave: int) -> int:
    '''convert a note number and octave numer to a note number; called by PageTools.process_user_input, PageTools._save_multi_settings,
    PageTools._set_toms_series and PageTools._set_multi_series'''
    number = 12 * (octave + 1) + note
    return number if 0 <= number <= 127 else _NONE

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
#         if 0 <= (number := 12 * octave + _NOTES.index(base_note)) <= 127:
#             return number