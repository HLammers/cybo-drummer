''' Library providing constant tuples for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024-2025 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

from data_types import ChainMapTuple, GenOptions

NOTES                = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')

import midi_tools as mt

_NONE                 = const(-1)

_FONT_FIRST_PAGE      = const(131)
_FONT_FIRST_ZONE      = const(145)
_FONT_FIRST_TRANSIENT = const(155)
_FONT_FIRST_CURVE     = const(163)
_FONT_FIRST_PATTERN   = const(178)

_PAGE_PROGRAM         = const(1)
_PAGE_MATRIX          = const(2)
_PAGE_INPUT           = const(3)
_PAGE_OUTPUT          = const(4)
_PAGE_TOOLS           = const(5)
_PAGE_MONITOR         = const(6)
_PAGE_SETTINGS        = const(7)

_ICON_PROGRAM         = chr(_FONT_FIRST_PAGE) + chr(_FONT_FIRST_PAGE + 1)
_ICON_MATRIX          = chr(_FONT_FIRST_PAGE + 2) + chr(_FONT_FIRST_PAGE + 3)
_ICON_INPUT           = chr(_FONT_FIRST_PAGE + 4) + chr(_FONT_FIRST_PAGE + 5)
_ICON_OUTPUT          = chr(_FONT_FIRST_PAGE + 6) + chr(_FONT_FIRST_PAGE + 7)
_ICON_TOOLS           = chr(_FONT_FIRST_PAGE + 8) + chr(_FONT_FIRST_PAGE + 9)
_ICON_MONITOR         = chr(_FONT_FIRST_PAGE + 10) + chr(_FONT_FIRST_PAGE + 11)
_ICON_SETTINGS        = chr(_FONT_FIRST_PAGE + 12) + chr(_FONT_FIRST_PAGE + 13)

MAIN_FRAMES           = (_PAGE_PROGRAM, _PAGE_MATRIX, _PAGE_INPUT, _PAGE_OUTPUT, _PAGE_TOOLS, _PAGE_MONITOR, _PAGE_SETTINGS)
PAGE_LABELS           = (_ICON_PROGRAM, _ICON_MATRIX, _ICON_INPUT, _ICON_OUTPUT, _ICON_TOOLS, _ICON_MONITOR, _ICON_SETTINGS)

CONTEXT_MENU_ITEMS    = ('rename', 'move backward', 'move forward', 'move to...')

_NR_IN_PORTS          = const(6)
_NR_OUT_PORTS         = const(6)
_LAYOUT_COLS          = const(4)
_CHORDS_COLS          = const(3)

BLANK_LABEL          = '[blank]'
DEFAULT_PROGRAM_NAME = 'incognito'

EMPTY_OPTIONS_BLANK   = ('',)
EMPTY_OPTIONS_1       = ('_',)
EMPTY_OPTIONS_2       = ('__',)
EMPTY_OPTIONS_3       = ('___',)
EMPTY_OPTIONS_4       = ('____',)
START_OPTION          = ('[start]',)

_ICON_CENTER          = chr(_FONT_FIRST_ZONE)
_ICON_RIM_EDGE        = chr(_FONT_FIRST_ZONE + 1)
_ICON_BOW             = chr(_FONT_FIRST_ZONE + 2)
_ICON_BELL            = chr(_FONT_FIRST_ZONE + 3)
_ICON_CHOKE           = chr(_FONT_FIRST_ZONE + 4)
_ICON_FOOT            = chr(_FONT_FIRST_ZONE + 5)
_ICON_LAYER_A         = chr(_FONT_FIRST_ZONE + 6)
_ICON_LAYER_B         = chr(_FONT_FIRST_ZONE + 7)
_ICON_LAYER_C         = chr(_FONT_FIRST_ZONE + 8)
_ICON_LAYER_D         = chr(_FONT_FIRST_ZONE + 9)
_SINGLE_OPT           = (EMPTY_OPTIONS_BLANK, EMPTY_OPTIONS_BLANK)
_PAD_OPT              = ((_ICON_CENTER, _ICON_RIM_EDGE), ('center', 'rim'))
_HIHAT_OPT            = ((_ICON_RIM_EDGE, _ICON_CENTER, _ICON_FOOT), ('edge', 'bow', 'foot'))
_CYMB_OPT             = ((_ICON_RIM_EDGE, _ICON_BOW, _ICON_BELL, _ICON_CHOKE), ('edge', 'bow', 'bell', 'choke'))
_MULTI_OPT            = ((_ICON_LAYER_A, _ICON_LAYER_B, _ICON_LAYER_C, _ICON_LAYER_D), ('layer A', 'layer B', 'layer C', 'layer D'))

_ICON_HARD            = chr(_FONT_FIRST_TRANSIENT) + chr(_FONT_FIRST_TRANSIENT + 1)
_ICON_SMOOTH_1        = chr(_FONT_FIRST_TRANSIENT + 2) + chr(_FONT_FIRST_TRANSIENT + 3)
_ICON_SMOOTH_2        = chr(_FONT_FIRST_TRANSIENT + 4) + chr(_FONT_FIRST_TRANSIENT + 5)
_ICON_LINEAR_TRANS    = chr(_FONT_FIRST_TRANSIENT + 6) + chr(_FONT_FIRST_TRANSIENT + 7)

_ICON_NEGATIVE_3      = chr(_FONT_FIRST_CURVE) + chr(_FONT_FIRST_CURVE + 1) + ' negative 3'
_ICON_NEGATIVE_2      = chr(_FONT_FIRST_CURVE + 2) + chr(_FONT_FIRST_CURVE + 3) + ' negative 2'
_ICON_NEGATIVE_1      = chr(_FONT_FIRST_CURVE + 4) + chr(_FONT_FIRST_CURVE + 5) + ' negative 1'
_ICON_LINEAR_CURVE    = chr(_FONT_FIRST_CURVE + 6) + chr(_FONT_FIRST_CURVE + 7) + ' linear    '
_ICON_POSITIVE_1      = chr(_FONT_FIRST_CURVE + 8) + chr(_FONT_FIRST_CURVE + 9) + ' positive 1'
_ICON_POSITIVE_2      = chr(_FONT_FIRST_CURVE + 10) + chr(_FONT_FIRST_CURVE + 11) + ' positive 2'
_ICON_POSITIVE_3      = chr(_FONT_FIRST_CURVE + 12) + chr(_FONT_FIRST_CURVE + 13) + ' positive 3'

_ICON_UP_RIGHT        = chr(_FONT_FIRST_PATTERN) + chr(_FONT_FIRST_PATTERN + 1)
_ICON_RIGHT_UP        = chr(_FONT_FIRST_PATTERN + 2) + chr(_FONT_FIRST_PATTERN + 3)

TRIGGERS = ( # (short label, long label, zone options)
    ('BD', 'base drum', _SINGLE_OPT), ('B2', 'base drum 2', _SINGLE_OPT), ('SD', 'snare drum', _PAD_OPT),
    ('T1', 'tom 1', _PAD_OPT), ('T2', 'tom 2', _PAD_OPT), ('T3', 'tom 3', _PAD_OPT),
    ('T4', 'tom 4', _PAD_OPT), ('T5', 'tom 5', _PAD_OPT), ('T6', 'tom 6', _PAD_OPT),
    ('T7', 'tom 7', _PAD_OPT), ('T8', 'tom 8', _PAD_OPT), ('T9', 'tom 9', _PAD_OPT),
    ('P1', 'percussion 1', _PAD_OPT), ('P2', 'percussion 2', _PAD_OPT), ('P3', 'percussion 3', _PAD_OPT),
    ('P4', 'percussion 4', _PAD_OPT), ('P5', 'percussion 5', _PAD_OPT), ('P6', 'percussion 6', _PAD_OPT),
    ('P7', 'percussion 7', _PAD_OPT), ('P8', 'percussion 8', _PAD_OPT), ('P9', 'percussion 9', _PAD_OPT),
    ('HO', 'open hihat', _HIHAT_OPT), ('HH', 'half-open hihat', _HIHAT_OPT), ('HC', 'closed hihat', _HIHAT_OPT),
    ('RD', 'ride cymbal', _CYMB_OPT),
    ('C1', 'crash/cymbal 1', _CYMB_OPT), ('C2', 'crash/cymbal 2', _CYMB_OPT), ('C3', 'crash/cymbal 3', _CYMB_OPT),
    ('C4', 'crash/cymbal 4', _CYMB_OPT), ('C5', 'crash/cymbal 5', _CYMB_OPT), ('C6', 'crash/cymbal 6', _CYMB_OPT),
    ('C7', 'crash/cymbal 7', _CYMB_OPT), ('C8', 'crash/cymbal 8', _CYMB_OPT), ('C9', 'crash/cymbal 9', _CYMB_OPT),
    ('M1', 'multipad 1', _MULTI_OPT), ('M2', 'multipad 2', _MULTI_OPT), ('M3', 'multipad 3', _MULTI_OPT),
    ('M4', 'multipad 4', _MULTI_OPT), ('M5', 'multipad 5', _MULTI_OPT), ('M6', 'multipad 6', _MULTI_OPT),
    ('M7', 'multipad 7', _MULTI_OPT), ('M8', 'multipad 8', _MULTI_OPT), ('M9', 'multipad 9', _MULTI_OPT),
    ('MA', 'multipad 10', _MULTI_OPT), ('MB', 'multipad 11', _MULTI_OPT), ('MC', 'multipad 12', _MULTI_OPT),
    ('A1', 'additional trig. 1', _PAD_OPT), ('A2', 'additional trig. 2', _PAD_OPT), ('A3', 'additional trig. 3', _PAD_OPT),
    ('A4', 'additional trig. 4', _PAD_OPT), ('A5', 'additional trig. 5', _PAD_OPT), ('A6', 'additional trig. 6', _PAD_OPT),
    ('A7', 'additional trig. 7', _PAD_OPT), ('A8', 'additional trig. 8', _PAD_OPT), ('A9', 'additional trig. 9', _PAD_OPT))
TRIGGERS_SHORT = tuple(t[0] for t in TRIGGERS)
TRIGGERS_LONG  = tuple(t[1] for t in TRIGGERS)
TOMS_INTERVALS = (
    (   # 2 toms
    'perfect fourth', (0, 5),
    'perfect fifth', (0, 7),
    'major sixth', (0, 9)
    ), ( # 3 toms
    'major thirds', (0, 4, 8),
    'perfect fourths', (0, 5, 10),
    'perfect fifths', (0, 7, 14)
    ), ( # 4 toms
    'major thirds', (0, 4, 8, 12),
    'P4/P4/M3', (0, 4, 9, 14),
    'perfect fourths', (0, 5, 10, 15),
    '2x P4', (0, 5, 12, 17),
    'P4/P5/P5', (0, 7, 12, 17)
    ))
TOMS_CHORDS = (
    (   # 2 toms
    ), ( # 3 toms
    'diminished', (0, 3, 6),
    'minor', (0, 3, 7),
    'major ', (0, 4, 7),
    'major (1st inv)', (0, 3, 8),
    'augmented', (0, 4, 8),
    'minor (2nd inv)', (0, 5, 8),
    'minor (1st inv)', (0, 4, 9),
    'major (2nd inv)', (0, 5, 9),
    'minor 7 (no 5)', (0, 3, 10),
    'major 7 (no 5)', (0, 4, 11)
    ), ( # 4 toms
    'diminished 7', (0, 3, 6, 9),
    'minor 6', (0, 3, 7, 9),
    'major 6', (0, 4, 7, 9),
    'half-dim 7', (0, 3, 6, 10),
    'minor 7', (0, 3, 7, 10),
    'dominant 7', (0, 4, 7, 10),
    'augmented 7', (0, 4, 8, 10),
    'major 7', (0, 4, 7, 11),
    'minor/major 7', (0, 3, 7, 11),
    'minor', (0, 5, 8, 12),
    'major ', (0, 5, 9, 12)
    ))
MULTI_LAYOUTS = (
    '4 pads 2x2', 2, 2, ((2, 3, _NONE, _NONE), (0, 1, _NONE, _NONE), (_NONE, _NONE, _NONE, _NONE), (_NONE, _NONE, _NONE, _NONE)),
    '6 pads 2x3', 2, 3, ((3, 4, 5, _NONE), (0, 1, 2, _NONE), (_NONE, _NONE, _NONE, _NONE), (_NONE, _NONE, _NONE, _NONE)),
    '8 pads 2x4', 2, 4, ((4, 5, 6, 7), (0, 1, 2, 3), (_NONE, _NONE, _NONE, _NONE), (_NONE, _NONE, _NONE, _NONE)),
    '8 pads 2x3+2', 3, 3, ((6, _NONE, 7, _NONE), (3, 4, 5, _NONE), (0, 1, 2, _NONE), (_NONE, _NONE, _NONE, _NONE)),
    '9 pads 3x3', 3, 3, ((6, 7, 8, _NONE), (3, 4, 5, _NONE), (0, 1, 2, _NONE, _NONE), (_NONE, _NONE, _NONE)),
    '10 pads 2+2x4', 3, 4, ((6, 7, 8, 9), (2, 3, 4, 5), (0, _NONE, _NONE, 1), (_NONE, _NONE, _NONE, _NONE)),
    '12 pads 4x3', 4, 3, ((9, 10, 11, _NONE), (6, 7, 8, _NONE), (3, 4, 5, _NONE), (0, 1, 2, _NONE)))
MULTI_SCALES = (
    '5t pentatonic major', (0, 2, 4, 7, 8),
    '5t pentatonic minor', (0, 3, 5, 7, 10),
    '5t in', (0, 1, 5, 7, 8),
    '5t yo', (0, 2, 5, 7, 9),
    '5t hirajoshi', (0, 4, 6, 7, 11),
    '5t iwato', (0, 1, 5, 6, 10),
    '5t insen', (0, 1, 5, 7, 10),
    '6t blues', (0, 3, 5, 6, 7, 10),
    '6t augmented', (0, 3, 4, 7, 8, 11),
    '6t whole note', (0, 2, 4, 6, 8, 10),
    '7t major', (0, 2, 4, 5, 7, 9, 11),
    '7t natural minor', (0, 2, 3, 5, 7, 8, 10),
    '7t harmonic minor', (0, 2, 3, 5, 7, 8, 11),
    '7t asc melodic minor', (0, 2, 3, 5, 7, 9, 11),
    '7t harmonic major', (0, 2, 4, 5, 7, 8, 11),
    '7t double harmonic', (0, 1, 4, 5, 7, 8, 11),
    '7t altered', (0, 1, 3, 4, 6, 8, 10),
    '7t hungarian minor', (0, 2, 3, 6, 7, 8, 11),
    '7t hungarian major', (0, 3, 4, 6, 7, 9, 10),
    '7t locrian major', (0, 2, 4, 5, 6, 8, 10),
    '7t ukrainian dorian', (0, 2, 3, 6, 7, 9, 10),
    '7t phrygian dominant', (0, 1, 4, 5, 7, 8, 10),
    '7t acoustic', (0, 2, 4, 6, 7, 9, 10),
    '7t persian', (0, 1, 4, 5, 6, 8, 11),
    '7t half diminished', (0, 2, 3, 5, 6, 8, 10),
    '7t lydian augmented', (0, 2, 4, 6, 8, 9, 11),
    '8t octatonic (I)', (0, 2, 3, 5, 6, 7, 8, 11),
    '8t octatonic (II)', (0, 1, 3, 4, 6, 7, 9, 10),
    '8t bebop dominant', (0, 2, 4, 6, 7, 9, 10, 11),
    '8t bebop major', (0, 2, 4, 5, 7, 8, 9, 11),
    '8t bebop mel minor', (0, 2, 3, 5, 7, 8, 9, 11),
    '8t bebop harm minor', (0, 2, 3, 5, 7, 9, 10, 11),
    '8t 7th flat 5 dim', (0, 2, 4, 5, 6, 9, 10, 11),
    '9t melodic minor', (0, 2, 3, 5, 7, 8, 9, 10, 11),
    '12t chromatic', (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
    'ionian mode (I)', (0, 2, 4, 5, 7, 9, 11),
    'dorian mode (II)', (0, 2, 3, 5, 7, 9, 10),
    'phrygian mode (III)', (0, 1, 3, 5, 7, 8, 10),
    'lydian mode (IV)', (0, 2, 4, 6, 7, 9, 11),
    'mixolydian mode (V)', (0, 2, 4, 5, 7, 9, 10),
    'aeolian mode (VI)', (0, 2, 3, 5, 7, 8, 10),
    'locrian mode (VII)', (0, 1, 3, 5, 6, 8, 10),
    'flamenco mode', (0, 1, 4, 5, 7, 8, 11))
MULTI_CHORDS = (
    '', 'major', (0, 4, 7),
    'm', 'minor', (0, 3, 7),
    '5', "fifth ('power chord')", (0, 7),
    '7', 'dominant seventh', (0, 4, 7, 10),
    'M7', 'major seventh', (0, 4, 7, 11),
    'm7', 'minor seventh', (0, 3, 7, 10),
    'mM7', 'minor major seventh', (0, 3, 7, 11),
    'sus', 'suspended fourth', (0, 5, 7),
    'sus2', 'suspended second', (0, 2, 7),
    '7sus', 'dominant 7th susp. 4th', (0, 5, 7, 10),
    '7s2', 'dominant 7th susp. 2nd', (0, 2, 7, 10),
    'add2', 'major added-second', (0, 2, 4, 7),
    'add9', 'major added-ninth', (0, 4, 7, 14),
    'add4', 'major added-fourth', (0, 4, 5, 7),
    'a11', 'major added-eleventh', (0, 4, 7, 17),
    'ma2', 'minor added-second', (0, 3, 4, 7),
    'ma9', 'minor added-ninth', (0, 3, 7, 14),
    'ma4', 'minor added-fourth', (0, 3, 5, 7),
    'ma11', 'minor added-eleventh', (0, 3, 7, 17),
    's4a2', 'suspended 4th added-2nd', (0, 2, 5, 7),
    's4a9', 'suspended 4th added-9th', (0, 5, 7, 14),
    '6', 'major sixth', (0, 4, 7, 9),
    'm6', 'minor sixth', (0, 3, 7, 9),
    'dim', 'diminished', (0, 3, 6),
    'dim7', 'deminished seventh', (0, 3, 6, 9),
    'aug', 'augmented', (0, 4, 8),
    '7b5', 'dominant 7th flat 5', (0, 4, 6, 10),
    '7#5', '7th sharp 5 / augmented 7th', (0, 4, 8, 10),
    'm7b5', 'minor 7 flat 5/half dim 7th', (0, 3, 6, 10),
    'M7#5', 'major 7th sharp 5', (0, 4, 8, 11),
    'm7#5', 'minor 7th sharp 5', (0, 3, 8, 10))

BANK_OPTIONS          = GenOptions(129, 0, EMPTY_OPTIONS_3, func=str)
CC_OPTIONS            = GenOptions(129, 1, EMPTY_OPTIONS_3, func=str)
CC_VALUE_OPTIONS      = GenOptions(128, func=str)
CHANNEL_OPTIONS       = GenOptions(17, 1, EMPTY_OPTIONS_2, func=str)
CURVE_OPTIONS         = (_ICON_NEGATIVE_3, _ICON_NEGATIVE_2, _ICON_NEGATIVE_1, _ICON_LINEAR_CURVE,
                         _ICON_POSITIVE_1, _ICON_POSITIVE_2, _ICON_POSITIVE_3)
INVERSION_OPTIONS     = ('root position', '1st inversion', '2nd inversion', '3rd inversion')
INPUT_PORT_OPTIONS    = GenOptions(_NR_IN_PORTS + 1, 1, EMPTY_OPTIONS_1, func=str)
KEY_OPTIONS           = ChainMapTuple(EMPTY_OPTIONS_2, NOTES)
LAYER_OPTIONS_W       = ('all', 'low', 'high')
LAYER_OPTIONS_WO      = ('low', 'high')
LAYOUT_OPTIONS        = GenOptions(len(MULTI_LAYOUTS) // _LAYOUT_COLS, func=lambda i: MULTI_LAYOUTS[_LAYOUT_COLS * i])
MODE_OPTIONS          = ('____', 'note', 'chord')
NOTE_OFF_OPTIONS_W    = GenOptions(925, 80, ('____', 'off', 'pulse', 'toggle'), func=str, suffix=' ms')
NOTE_OFF_OPTIONS_WO   = GenOptions(924, 80, ('off', 'pulse', 'toggle'), func=str, suffix=' ms')
NOTE_OPTIONS          = GenOptions(129, first_options=EMPTY_OPTIONS_3, func=mt.number_to_note)
OCTAVE_OPTIONS        = GenOptions(12, -1, EMPTY_OPTIONS_2, func=str)
OUTPUT_PORT_OPTIONS   = GenOptions(_NR_OUT_PORTS + 1, 1, EMPTY_OPTIONS_1, func=str)
PATTERN_OPTIONS       = (('__', _ICON_UP_RIGHT, _ICON_RIGHT_UP),
                         ('select assignment pattern', 'assign notes up and then rigt', 'assign notes right and than up'))
PC_OPTIONS            = GenOptions(129, 0, EMPTY_OPTIONS_3, func=str)
QUALITY_OPTIONS_LONG  = GenOptions(len(MULTI_CHORDS) // _CHORDS_COLS + 1, first_options=EMPTY_OPTIONS_4,
                                  func=lambda i: MULTI_CHORDS[_CHORDS_COLS * i + 1])
QUALITY_OPTIONS_SHORT = GenOptions(len(MULTI_CHORDS) // _CHORDS_COLS + 1, first_options=EMPTY_OPTIONS_BLANK,
                                   func=lambda i: MULTI_CHORDS[_CHORDS_COLS * i])
SCALE_OPTIONS         = GenOptions(len(MULTI_SCALES) // 2 + 1, first_options=EMPTY_OPTIONS_4, func=lambda i: MULTI_SCALES[2 * i])
TRANSIENT_OPTIONS     = (('__', _ICON_HARD, _ICON_SMOOTH_1, _ICON_SMOOTH_2, _ICON_LINEAR_TRANS),
                         ('transient off', 'hard transient', 'smooth transient 1', 'smooth transient 2', 'linear transient'))
TRIGGER_OPTIONS_LONG  = ChainMapTuple(EMPTY_OPTIONS_4, TRIGGERS_LONG)
TRIGGER_OPTIONS_SHORT = ChainMapTuple(EMPTY_OPTIONS_BLANK, TRIGGERS_SHORT)
VELOCITY_OPTIONS      = GenOptions(128, func=str)

TEXT_ROWS_PROGRAM = (( # _SUB_PAGE_MAPPING
    'active program', # _NAME
    'selected input trigger' # _INPUT_TRIGGER
), ( # _SUB_PAGE_NOTE
    'active program', # _NAME
    'selected input trigger' # _INPUT_TRIGGER
))

TEXT_ROWS_INPUT = (( # _SUB_PAGE_PORTS
    'device name for input port 1', # _PORT_FIRST_DEVICE
    'channel to receive on for port 1', # _PORT_FIRST_CHANNEL
    'device name for input port 2', # _PORT_FIRST_DEVICE + 2
    'channel to receive on for port 2', # _PORT_FIRST_CHANNEL + 2
    'device name for input port 3', # _PORT_FIRST_DEVICE + 4
    'channel to receive on for port 3', # _PORT_FIRST_CHANNEL + 4
    'device name for input port 4', # _PORT_FIRST_DEVICE + 6
    'channel to receive on for port 4', # _PORT_FIRST_CHANNEL + 6
    'device name for input port 5', # _PORT_FIRST_DEVICE + 8
    'channel to receive on for port 5', # _PORT_FIRST_CHANNEL + 8
    'device name for input port 6', # _PORT_FIRST_DEVICE + 10
    'channel to receive on for port 6', # _PORT_FIRST_CHANNEL + 10
), ( # _SUB_PAGE_NOTES
    'selected input trigger', # _NOTE_INPUT_TRIGGER
    'input port/device assigned to '# _NOTE_DEVICE
))

TEXT_ROWS_OUTPUT = (( # _SUB_PAGE_PORTS
    'device name for output port 1', # _PORT_FIRST_DEVICE
    'device name for output port 2', # _PORT_FIRST_DEVICE + 1
    'device name for output port 3', # _PORT_FIRST_DEVICE + 2
    'device name for output port 4', # _PORT_FIRST_DEVICE + 3
    'device name for output port 5', # _PORT_FIRST_DEVICE + 4
    'device name for output port 6', # _PORT_FIRST_DEVICE + 5
), ( # _SUB_PAGE_DEVICE:
    'selected output port/device', # _DEVICE_DEVICE
    'midi channel to use', # _DEVICE_CHANNEL
    'use 0 velocity for note off', # _DEVICE_0_NOTE_OFF
    'enable running status', # _DEVICE_RUNNING_STATUS
), ( # _SUB_PAGE_VOICE
    'selected output port/device', # _VOICE_DEVICE
    '', # _VOICE_VOICE
    'midi channel to use', # _VOICE_CHANNEL
    'assigned midi note', #_VOICE_NOTE
    'set note off behaviour', # _VOICE_NOTE_OFF
    'velocity threshold (ignore below)', # _VOICE_THRESHOLD
    'velocity response curve', # _VOICE_CURVE
    'minimum output velocity', # _VOICE_MIN_VELOCITY
    'maximum output velocity', # _VOICE_MAX_VELOCITY
))

TEXT_ROWS_TOOLS = (( # _SUB_PAGE_TOMS
    'select which tom zone to edit', #_TOMS_ZONE
    'select interval to assign', # _TOMS_INTERVAL
    'select chord to assign', # _TOMS_CHORD
    'lowest tom note', # _TOMS_NOTE
    'octave of lowest note', # _TOMS_OCTAVE
    'shift all notes up one semitone', # _TOMS_NOTE_UP
    'shift all notes down one semitone', # _TOMS_NOTE_DOWN
    'shift all notes up one octave', # _TOMS_OCTAVE_UP
    'shift all notes down one octave', # _TOMS_OCTAVE_DOWN
    'set inclusion of tom 1', # _TOMS_FIRST_CHECK
    'set inclusion of tom 2', # _TOMS_FIRST_CHECK + 1
    'set inclusion of tom 3', # _TOMS_FIRST_CHECK + 2
    'set inclusion of tom 4', # _TOMS_FIRST_CHECK + 3
    'set note for tom 1', # _TOMS_FIRST_NOTE
    'set note for tom 2', # _TOMS_FIRST_NOTE + 1
    'set note for tom 3', # _TOMS_FIRST_NOTE + 2
    'set note for tom 4', # _TOMS_FIRST_NOTE + 3
), ( # _SUB_PAGE_MULTIPAD
    'select which m.pad layer to edit', # _MULTIPAD_ZONE
    'set all pads to note mode', # _MULTIPAD_ALL_NOTES
    'set all pads to chord mode', # _MULTIPAD_ALL_CHORDS
    'set mode to off, note or chord', # _MULTIPAD_FIRST_MODE
), ( # _SUB_PAGE_MULTI_NOTE:
    'select voice velocity layer', # _MULTI_LAYER
    'select scale to assign', # _MULTI_SCALE
    '', # _MULTI_PATTERN
    'select key to assign', # _MULTI_KEY
    'octave of lowest note', # _MULTI_OCTAVE
    'shift notes one step down or up', # _MULTI_SHIFT
), ( # sub_page == _SUB_PAGE_MULTI_CHORD
    'shift all notes up one semitone', # _MULTI_NOTE_UP
    'shift all notes down one semitone', # _MULTI_NOTE_DOWN
    'shift all notes up one octave', # _MULTI_OCTAVE_UP
    'shift all notes down one octave', # _MULTI_OCTAVE_DOWN
))

TEXT_ROWS_SETTINGS = (
'enable midi thru', # _MIDI_THRU
'midi thru input port', # _MIDI_THRU_INPUT_PORT
'midi thru input channel', # _MIDI_THRU_INPUT_CHANNEL
'midi thru output port', # _MIDI_THRU_OUTPUT_PORT
'midi thru output channel', # _MIDI_THRU_OUTPUT_CHANNEL
'enable midi learn', # _MIDI_LEARN
'input port to use for midi learn', # _MIDI_LEARN_PORT
'default volume for output voices', # _DEFAULT_VELOCITY
'back up settings and programs', # _STORE_BACK_UP
'restore backed up data', # _RESTORE_BACK_UP
'clear user settings to defaults', # _FACTORY_RESET
'show cybo-drummer version number', # _OTHER_ABOUT
)