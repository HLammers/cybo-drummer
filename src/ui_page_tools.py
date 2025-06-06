''' Library providing tools pages class for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024-2025 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

_INITIAL_SUB_PAGE = const(0)

import main_loops as ml
from data_types import GenOptions
import midi_tools as mt
from ui_pages import Page
from ui_blocks import TitleBar, EmptyBlock, ButtonBlock, CheckBoxBlock, SelectBlock, TextBlock, TextRow
from constants import EMPTY_OPTIONS_4, TOMS_INTERVALS, TOMS_CHORDS, MULTI_LAYOUTS, MULTI_SCALES, MULTI_CHORDS, TRIGGERS, TRIGGERS_SHORT, \
    NOTE_OPTIONS, KEY_OPTIONS, LAYER_OPTIONS_W, OCTAVE_OPTIONS, MODE_OPTIONS, PATTERN_OPTIONS, SCALE_OPTIONS, QUALITY_OPTIONS_SHORT, \
    TEXT_ROWS_TOOLS

_NONE                 = const(-1)
_OCTAVE_NONE          = const(-2)

_ASCII_A              = const(65)
_ICON_UP              = chr(176)
_ICON_DOWN            = chr(177)

_ENCODER_VAL          = const(1)

_MATRIX_ROWS          = const(8)
_MATRIX_COLUMNS       = const(8)
_MAX_TOMS             = const(4)
_MAX_MULTI_ROWS       = const(4)
_MAX_MULTI_COLUMNS    = const(4)
_MULTI_CHORD_COLUMNS  = const(3)

_MAX_SCALE_LENGTH     = const(12)

_TEXT_ROW_Y           = const(163)
_TEXT_ROW_H           = const(13)

_BACK_COLOR           = const(0xAA29) # 0x29AA dark purple blue
_FORE_COLOR           = const(0xD9CD) # 0xCDD9 light purple grey

_ALIGN_CENTRE         = const(1)

_MODE_OFF             = const(0)
_MODE_NOTE            = const(1)
_MODE_CHORD           = const(2)

_PATTERN_NONE         = const(0)
_PATTERN_UP_RIGHT     = const(1)
_PATTERN_RIGHT_UP     = const(2)

_MIN_TOMS             = const(2)
_FIRST_PAD            = const(34)

_SUB_PAGES            = const(4)
_SUB_PAGE_TOMS        = const(0)
_SUB_PAGE_MULTIPAD    = const(1)
_SUB_PAGE_MULTI_NOTE  = const(2)
_SUB_PAGE_MULTI_CHORD = const(3)

_SELECT_SUB_PAGE      = const(-1)
_TOMS_ZONE            = const(0)
_TOMS_INTERVAL        = const(1)
_TOMS_CHORD           = const(2)
_TOMS_NOTE            = const(3)
_TOMS_OCTAVE          = const(4)
_TOMS_NOTE_UP         = const(5)
_TOMS_NOTE_DOWN       = const(6)
_TOMS_OCTAVE_UP       = const(7)
_TOMS_OCTAVE_DOWN     = const(8)
_TOMS_FIRST_CHECK     = const(9)
_TOMS_FIRST_NOTE      = const(13)
_MULTIPAD_ZONE        = const(0)
_MULTIPAD_ALL_NOTES   = const(1)
_MULTIPAD_ALL_CHORDS  = const(2)
_MULTIPAD_FIRST_MODE  = const(3)
_MULTIPAD_MAX         = const(15)

_MULTI_LAYER          = const(0)
_MULTI_SCALE          = const(1)
_MULTI_PATTERN        = const(2)
_MULTI_KEY            = const(3)
_MULTI_OCTAVE         = const(4)
_MULTI_SHIFT          = const(5)
_MULTI_FIRST_PAD      = const(6)
_MULTI_NOTE_UP        = const(0)
_MULTI_NOTE_DOWN      = const(1)
_MULTI_OCTAVE_UP      = const(2)
_MULTI_OCTAVE_DOWN    = const(3)
_MULTI_CHORD_FIRST    = const(4)

_TOMS_ROUTE_COL       = const(0)
_TOMS_TRIGGER_COL     = const(1)
_TOMS_CHECKED_COL     = const(2)
_TOMS_NOTE_COL        = const(3)

_MULTI_ROUTE_COL      = const(0)
_MULTI_TRIGGER_COL    = const(1)
_MULTI_MODE_COL       = const(2)
_MULTI_VALUE_COL      = const(3)

_LAYOUT_ROWS          = const(4)
_LAYOUT_COLS          = const(4)
_LAYOUT_ROWS_COL      = const(1)
_LAYOUT_COLS_COL      = const(2)
_LAYOUT_MAP_COL       = const(3)
_LAYOUT_MAP_COLS      = const(4)

_CHORD_ROOT           = const(0)
_CHORD_OCTAVE         = const(1)
_CHORD_QUALITY        = const(2)
_CHORD_INVERSION      = const(3)

_POP_UP_CHORD         = const(8)

_LAYER_ALL            = const(0)
_LAYER_LOW            = const(1)
_LAYER_HIGH           = const(2)
_TRANSIENT_LAYER_LOW  = const(0)
_TRANSIENT_LAYER_HIGH = const(1)

_DEFAULT_LAYOUT       = const(2)

class PageTools(Page):
    '''tools page class; initiated once by ui.__init__'''

    def __init__(self, id: int, x: int, y: int, w: int, h: int, visible: bool) -> None:
        super().__init__(id, x, y, w, h, 
        _SUB_PAGES, visible)
        self.sub_page = _INITIAL_SUB_PAGE
        self.base_tom = _NONE
        self.toms_zone = 0
        self.toms_interval = _NONE
        self.toms_chord = _NONE
        self.toms_note = _NONE
        self.toms_octave = _OCTAVE_NONE
        self.toms_settings = [[None, _NONE, False, _NONE] for _ in range(_MAX_TOMS)]
        self.nr_tom_triggers = _NONE
        self.nr_toms = 0
        self.toms_initiated = False
        self.multi_zone = 0
        self.multi_voice_layer = _LAYER_ALL
        self.multi_layout = 1
        self.base_multi_note = _NONE
        self.base_multi_chord = _NONE
        self.multi_scale = _NONE
        self.multi_pattern = _PATTERN_NONE
        self.multi_key = _NONE
        self.multi_octave = _OCTAVE_NONE
        self.multi_shift = 0
        self.middle_shift = 0
        self.multi_settings = [[[None, _NONE, _MODE_OFF, None] for _ in range(_LAYOUT_COLS)] for _ in range(_LAYOUT_ROWS)]
        self.multi_initiated = False
        self.page_is_built = False
        self._build_page()

    def program_change(self, update_only: bool) -> None:
        '''update page after program change; called by ui.program_change'''
        if not update_only:
            self.multi_initiated = False
        if self.visible:
            if not update_only:
                if self.sub_page == _SUB_PAGE_TOMS:
                    self._initiate_toms()
                else:
                    self._initiate_multipad()
            self._load()
        else:
            if (selected_block := self.selected_block[self.sub_page]) != 0:
                blocks = self.blocks
                blocks[selected_block].update(False, False)
                blocks[0].update(True, False)

    def encoder(self, encoder_id: int, value: int, page_select_mode: bool) -> bool:
        '''process encoder input at page level (ui.process_encoder > Page.encoder/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by ui.process_encoder_input'''
        if super().encoder(encoder_id, value, page_select_mode):
            if encoder_id == _ENCODER_VAL:
                self._set_text_row(value)
            else:
                self._set_text_row()
            return True
        return False

    def process_user_input(self, id: int, value: int|str = _NONE, button_del: bool = False, button_sel_opt: bool = False) -> bool:
        '''process user input at page level (ui.set_user_input_tuple > ui.user_input_tuple > ui.process_user_input >
        Page/PagesTab.process_user_input); called by ui.process_user_input'''
        value = int(value)
        sub_page = self.sub_page
        if id == _SELECT_SUB_PAGE:
            if button_del or button_sel_opt or value == _NONE or value == sub_page:
                return False
            self._set_sub_page(value)
            self._load()
            return True
        if sub_page == _SUB_PAGE_TOMS:
            if button_del:
                return False
            reidentify = False
            if button_sel_opt:
                if id == _TOMS_NOTE_DOWN:
                    for setting in self.toms_settings:
                        note = setting[_TOMS_NOTE_COL]
                        if not setting[_TOMS_CHECKED_COL] or note == _NONE:
                            continue
                        setting[_TOMS_NOTE_COL] -= 1
                        reidentify = True
                elif id == _TOMS_NOTE_UP:
                    for setting in self.toms_settings:
                        note = setting[_TOMS_NOTE_COL]
                        if not setting[_TOMS_CHECKED_COL] or note == _NONE:
                            continue
                        if note == 127:
                            setting[_TOMS_NOTE_COL] = _NONE
                        else:
                            setting[_TOMS_NOTE_COL] += 1
                        reidentify = True
                elif id == _TOMS_OCTAVE_DOWN:
                    for setting in self.toms_settings:
                        note = setting[_TOMS_NOTE_COL]
                        if not setting[_TOMS_CHECKED_COL] or note == _NONE:
                            continue
                        if note < 12:
                            setting[_TOMS_NOTE_COL] = _NONE
                        else:
                            setting[_TOMS_NOTE_COL] -= 12
                        reidentify = True
                elif id == _TOMS_OCTAVE_UP:
                    for setting in self.toms_settings:
                        note = setting[_TOMS_NOTE_COL]
                        if not setting[_TOMS_CHECKED_COL] or note == _NONE:
                            continue
                        if note > 115:
                            setting[_TOMS_NOTE_COL] = _NONE
                        else:
                            setting[_TOMS_NOTE_COL] += 12
                        reidentify = True
                else:
                    return False
            elif value == _NONE:
                return False
            elif id == _TOMS_ZONE:
                self.toms_zone = value
                self._initiate_toms()
                self._set_toms_options()
                self.blocks[self.selected_block[sub_page]].draw()
                return True
            elif id == _TOMS_INTERVAL:
                self.toms_interval = value - 1 # 0 becomes _NONE
                if not (reidentify := self._set_toms_series()):
                    self.toms_chord = _NONE
                    blocks = self.blocks
                    blocks[_TOMS_INTERVAL].draw()
                    blocks[_TOMS_CHORD].draw()
            elif id == _TOMS_CHORD:
                self.toms_chord = value - 1 # 0 becomes _NONE
                if not (reidentify := self._set_toms_series()):
                    self.toms_interval = _NONE
                    blocks = self.blocks
                    blocks[_TOMS_INTERVAL].draw()
                    blocks[_TOMS_CHORD].draw()
            elif id == _TOMS_NOTE or id == _TOMS_OCTAVE:
                not_empty = value != 0
                if id == _TOMS_NOTE:
                    value -= 1 # 0 becomes _NONE
                    self.toms_note = value
                else:
                    value -= 2 # 0 becomes _OCTAVE_NONE
                    self.toms_octave = value
                if not_empty:
                    if not (reidentify := self._set_toms_base_note(id, value)):
                        if id == _TOMS_NOTE:
                            self.blocks[_TOMS_NOTE].draw()
                        else:
                            self.blocks[_TOMS_OCTAVE].draw()
            elif id >= _TOMS_FIRST_CHECK:
                if id < _TOMS_FIRST_NOTE: # check box
                    settings = self.toms_settings
                    # reverse order because the typical tom setup is from high to low
                    settings[_MAX_TOMS - id + _TOMS_FIRST_CHECK - 1][_TOMS_CHECKED_COL] = bool(value)
                    self.nr_toms = sum(1 for setting in settings if setting[_TOMS_CHECKED_COL])
                else: # note
                    value -= 1 # 0 becomes _NONE
                    # reverse order because the typical tom setup is from high to low
                    self.toms_settings[_MAX_TOMS - id + _TOMS_FIRST_NOTE - 1][_TOMS_NOTE_COL] = value
            changed = self._save_toms_settings()
            if reidentify and not changed:
                self._identify_toms_parameters()
                self._set_toms_options()
                self.draw()
        else: # sub_page == _SUB_PAGE_MULTIPAD or sub_page == _SUB_PAGE_MULTI_NOTE or sub_page == _SUB_PAGE_MULTI_CHORD:
            if button_del:
                return False
            reidentify = False
            if sub_page == _SUB_PAGE_MULTIPAD:
                if button_sel_opt:
                    layouts = MULTI_LAYOUTS
                    multi_layout = self.multi_layout
                    if id == _MULTIPAD_ALL_NOTES:
                        for row, setting_row in enumerate(self.multi_settings):
                            for col, setting in enumerate(setting_row):
                                if setting[_MULTI_MODE_COL] == _MODE_NOTE or \
                                        layouts[multi_layout * _LAYOUT_COLS + _LAYOUT_MAP_COL][row][col] == _NONE: # type: ignore
                                    continue
                                setting[_MULTI_MODE_COL] = _MODE_NOTE
                                setting[_MULTI_VALUE_COL] = None
                                reidentify = True
                    elif id == _MULTIPAD_ALL_CHORDS:
                        for row, setting_row in enumerate(self.multi_settings):
                            for col, setting in enumerate(setting_row):
                                if setting[_MULTI_MODE_COL] == _MODE_CHORD or \
                                        layouts[multi_layout * _LAYOUT_COLS + _LAYOUT_MAP_COL][row][col] ==_NONE: # type: ignore
                                    continue
                                setting[_MULTI_MODE_COL] = _MODE_CHORD
                                setting[_MULTI_VALUE_COL] = None
                                reidentify = True
                    else:
                        return False
                elif value == _NONE:
                    return False
                elif id == _MULTIPAD_ZONE:
                    self.multi_zone = value
                    self._initiate_multipad()
                    self._set_multi_options()
                    self.blocks[self.selected_block[sub_page]].draw()
                    return True
                elif id >= _MULTIPAD_FIRST_MODE:
                    settings = self.multi_settings
                    row, col = divmod(id - _MULTIPAD_FIRST_MODE, _LAYOUT_COLS)
                    settings[row][col][_MULTI_MODE_COL] = value
                    reidentify = True
                changed = False
            elif sub_page == _SUB_PAGE_MULTI_NOTE:
                if button_sel_opt:
                    return False
                elif value == _NONE:
                    return False
                if id == _MULTI_LAYER:
                    if self.multi_voice_layer != value:
                        self.multi_voice_layer = value
                        reidentify = True
                    else:
                        self.blocks[_MULTI_LAYER].draw()
                elif id == _MULTI_SCALE:
                    self.multi_scale = value - 1 # 0 becomes _NONE
                    if not (reidentify := self._set_multi_series()):
                        self.blocks[_MULTI_SCALE].draw()
                elif id == _MULTI_PATTERN:
                    self.multi_pattern = value
                    reidentify =  self._set_multi_series()
                    if not reidentify:
                        self.blocks[_MULTI_PATTERN].draw()
                elif id == _MULTI_KEY or id == _MULTI_OCTAVE:
                    not_empty = value != 0
                    if id == _MULTI_KEY:
                        value -= 1 # 0 becomes _NONE
                        self.multi_key = value
                    else: # id == _MULTI_OCTAVE
                        value -= 2 # 0 becomes _OCTAVE_NONE
                        self.multi_octave = value
                    if not_empty:
                        if not(reidentify := self._set_multi_key(id, value)):
                            self.blocks[id].draw()
                elif id == _MULTI_SHIFT:
                    self.multi_shift = value - self.middle_shift
                    if not (reidentify := self._set_multi_series()):
                        self.blocks[id].draw()
                elif id >= _MULTI_FIRST_PAD:
                    n = id - _MULTI_FIRST_PAD
                    row, col = divmod(n, _LAYOUT_COLS)
                    value -= 1 # 0 becomes _NONE
                    self.multi_settings[row][col][_MULTI_VALUE_COL] = value
                    reidentify = True
                changed = self._save_multi_settings()
            else: # sub_page == _SUB_PAGE_MULTI_CHORD
                if button_sel_opt:
                    if id == _MULTI_NOTE_UP or id == _MULTI_NOTE_DOWN or id == _MULTI_OCTAVE_UP or id == _MULTI_OCTAVE_DOWN:
                        _mt = mt
                        _note_from_number_and_octave = _mt.note_from_number_and_octave
                        _number_to_base_note = _mt.number_to_base_note
                        _number_to_octave = _mt.number_to_octave
                        if id == _MULTI_NOTE_UP:
                            d = 1
                        elif id == _MULTI_NOTE_DOWN:
                            d = -1
                        elif id == _MULTI_OCTAVE_UP:
                            d = 12
                        else: # id == _MULTI_OCTAVE_DOWN
                            d = -12
                        for setting_row in self.multi_settings:
                            for setting in setting_row:
                                if setting[_MULTI_MODE_COL] != _MODE_CHORD:
                                    continue
                                if type(chord := setting[_MULTI_VALUE_COL]) is list:
                                    if (root := chord[_CHORD_ROOT]) == _NONE:
                                        continue
                                    note = _note_from_number_and_octave(root, chord[_CHORD_OCTAVE]) + d
                                    chord[_CHORD_ROOT] = _number_to_base_note(note)
                                    chord[_CHORD_OCTAVE] = _number_to_octave(note)
                        self._set_multi_options()
                    elif id >= _MULTI_CHORD_FIRST:
                        row, col = divmod((pad := id - _MULTI_CHORD_FIRST), _MAX_MULTI_COLUMNS)
                        setting = self.multi_settings[row][col]
                        if setting[_MULTI_MODE_COL] == _MODE_CHORD:
                            if not type(chord := setting[_MULTI_VALUE_COL]) is list:
                                chord = [_NONE, _OCTAVE_NONE, _NONE, 0]
                            ml.ui.pop_ups[_POP_UP_CHORD].open(self, pad, chord[_CHORD_ROOT], chord[_CHORD_OCTAVE],
                                chord[_CHORD_QUALITY], chord[_CHORD_INVERSION], callback_func=self._callback_chord)
                            return True
                        return False
                    else:
                        return False
                changed = self._save_multi_settings()
            if reidentify and not changed:
                self._identify_multi_parameters()
                self._set_multi_options()
                self._set_text_row(redraw=False)
                self.draw()
        return True

    def set_trigger(self) -> None:
        '''set active trigger (triggered by trigger button) at page level; called by ui.set_trigger (also calling router.set_trigger)'''
        self._load()

    def midi_learn(self, port: int, channel: int, trigger: int, zone: int, note: int, program: int, cc: int, cc_value: int) -> bool:
        '''process midi learn input, save settings and reload options; called by ui.process_midi_learn_data'''
        block = self.selected_block[(sub_page := self.sub_page)]
        set_toms_base = False
        set_multi_base = False
        if sub_page == _SUB_PAGE_TOMS:
            if block == _TOMS_NOTE:
                if note == _NONE:
                    return False
                value = mt.number_to_base_note(note) + 1 # _NONE becomes 0
                set_toms_base = True
            elif block == _TOMS_OCTAVE:
                if note == _NONE:
                    return False
                value = mt.number_to_octave(note) + 2 # _OCTAVE_NONE becomes 0
                set_toms_base = True
            elif block >= _TOMS_FIRST_NOTE:
                if note == _NONE:
                    return False
                value = note + 1 # _NONE becomes 0
            else:
                return False
        elif sub_page == _SUB_PAGE_MULTIPAD:
            return False
        elif sub_page == _SUB_PAGE_MULTI_NOTE:
            if block == _MULTI_KEY:
                if note == _NONE:
                    return False
                value = mt.number_to_base_note(note) + 1 # _NONE becomes 0
                set_multi_base = True
            elif block == _MULTI_OCTAVE:
                if note == _NONE:
                    return False
                value = mt.number_to_octave(note) + 2 # _OCTAVE_NONE becomes 0
                set_multi_base = True
            if block >= _MULTI_FIRST_PAD:
                if note == _NONE:
                    return False
                value = note + 1 # _NONE becomes 0
            else:
                return False
        else:
            return False
        redraw = self.blocks[block].set_selection(value)
        if set_toms_base:
            value = self.toms_note if block == _TOMS_NOTE else self.toms_octave
            if self._set_toms_base_note(block, value):
                self._identify_toms_parameters()
            else:
                self.blocks[block].draw()
            redraw = True
        if set_multi_base:
            value = self.multi_key if block == _MULTI_KEY else self.toms_octave
            if self._set_multi_key(block, value):
                self._identify_multi_parameters()
            else:
                self.blocks[block].draw()
            redraw = True
        return redraw

    def _build_page(self) -> None:
        '''build page (without drawing it); called by self.__init__ and self._build_sub_page'''
        if (sub_page := self.sub_page) is None or self.page_is_built:
            return
        self.page_is_built = True
        _build_sub_page = self._build_sub_page
        sub_pages_title_bars = self.sub_pages_title_bars
        sub_pages_blocks = self.sub_pages_blocks
        sub_pages_empty_blocks = self.sub_pages_empty_blocks
        sub_pages_text_rows = self.sub_pages_text_rows
        for i in range(_SUB_PAGES):
            title_bar, blocks, empty_blocks, text_row = _build_sub_page(i)
            sub_pages_title_bars.append(title_bar)
            sub_pages_blocks.append(blocks)
            sub_pages_empty_blocks.append(empty_blocks)
            sub_pages_text_rows.append(text_row)
        self._set_sub_page(sub_page)

    def _build_sub_page(self, sub_page: int) -> tuple:
        '''build sub-page (without drawing it); called by self._build_page'''
        if not self.page_is_built:
            self._build_page()
            return None, [], []
        blocks = []
        empty_blocks = []
        selected_block = self.selected_block[sub_page]
        _callback_input = self.callback_input
        if sub_page == _SUB_PAGE_TOMS:
            title_bar = TitleBar('assign toms', 1, _SUB_PAGES)
            blocks.append(SelectBlock(_TOMS_ZONE, 0, 0, 1, 1, selected_block == _TOMS_ZONE, 'center/rim',
                                      TRIGGERS[TRIGGERS_SHORT.index('T1')][2][1], default_selection=0, add_line=True,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_TOMS_INTERVAL, 1, 0, 1, 2, selected_block == _TOMS_INTERVAL, 'interval',
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_TOMS_CHORD, 1, 1, 1, 2, selected_block == _TOMS_CHORD, 'chord', callback_func=_callback_input))
            blocks.append(SelectBlock(_TOMS_NOTE, 2, 0, 1, 2, selected_block == _TOMS_NOTE, 'lowest note', KEY_OPTIONS,
                                      default_selection=0, callback_func=_callback_input))
            blocks.append(SelectBlock(_TOMS_OCTAVE, 2, 1, 1, 2, selected_block == _TOMS_OCTAVE, 'octave', OCTAVE_OPTIONS,
                                      default_selection=3, callback_func=_callback_input))
            blocks.append(ButtonBlock(_TOMS_NOTE_UP, 3, 0, 1, 4, selected_block == _TOMS_NOTE_UP, 'note ' + _ICON_UP,
                                      callback_func=_callback_input))
            blocks.append(ButtonBlock(_TOMS_NOTE_DOWN, 3, 1, 1, 4, selected_block == _TOMS_NOTE_DOWN, 'note ' + _ICON_DOWN,
                                      callback_func=_callback_input))
            blocks.append(ButtonBlock(_TOMS_OCTAVE_UP, 3, 2, 1, 4, selected_block == _TOMS_OCTAVE_UP, 'oct ' + _ICON_UP,
                                      callback_func=_callback_input))
            blocks.append(ButtonBlock(_TOMS_OCTAVE_DOWN, 3, 3, 1, 4, selected_block == _TOMS_OCTAVE_DOWN, 'oct ' + _ICON_DOWN,
                                      callback_func=_callback_input))
            for i in range(_MAX_TOMS):
                blocks.append(CheckBoxBlock(_TOMS_FIRST_CHECK + i, 4, i, 1, 4, selected_block == _TOMS_FIRST_CHECK + i,
                                            f'tom {i + 1}', callback_func=_callback_input))
            for i in range(_MAX_TOMS):
                blocks.append(SelectBlock(_TOMS_FIRST_NOTE + i, 5, i, 1, 4, selected_block == _TOMS_FIRST_NOTE + i, 'note',
                                          default_selection=0, callback_func=_callback_input))
        elif sub_page == _SUB_PAGE_MULTIPAD:
            title_bar = TitleBar('multipad: select mode', 2, _SUB_PAGES)
            blocks.append(SelectBlock(_MULTIPAD_ZONE, 0, 0, 1, 1, selected_block == _MULTIPAD_ZONE, 'multipad layer',
                                      TRIGGERS[TRIGGERS_SHORT.index('M1')][2][1], default_selection=0, add_line=True,
                                      callback_func=_callback_input))
            blocks.append(ButtonBlock(_MULTIPAD_ALL_NOTES, 1, 0, 1, 2, selected_block == _MULTIPAD_ALL_NOTES, 'all to note',
                                      callback_func=_callback_input))
            blocks.append(ButtonBlock(_MULTIPAD_ALL_CHORDS, 1, 1, 1, 2, selected_block == _MULTIPAD_ALL_CHORDS, 'all to chord',
                                      callback_func=_callback_input))
            for i in range(_MULTIPAD_MAX):
                row, col = divmod(i, _MAX_MULTI_COLUMNS)
                blocks.append(SelectBlock(_MULTIPAD_FIRST_MODE + i, 2 + row, col, 1, 4, selected_block == _MULTIPAD_FIRST_MODE + i,
                                          default_selection=0, callback_func=_callback_input))
            empty_blocks.append(EmptyBlock(5, 3, 1, 4))
        elif sub_page == _SUB_PAGE_MULTI_NOTE:
            title_bar = TitleBar('multipad: assign notes', 3, _SUB_PAGES)
            blocks.append(SelectBlock(_MULTI_LAYER, 0, 0, 1, 4, selected_block == _MULTI_LAYER, 'lo/hi', LAYER_OPTIONS_W,
                                      default_selection=0, callback_func=_callback_input))
            blocks.append(SelectBlock(_MULTI_SCALE, 0, 1, 3, 4, selected_block == _MULTI_SCALE, 'scale/mode', SCALE_OPTIONS,
                                      default_selection=11, callback_func=_callback_input))
            blocks.append(SelectBlock(_MULTI_PATTERN, 1, 0, 1, 4, selected_block == _MULTI_PATTERN, 'pattern', PATTERN_OPTIONS[0],
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_MULTI_KEY, 1, 1, 1, 4, selected_block == _MULTI_KEY, 'key', KEY_OPTIONS, default_selection=0,
                                      callback_func=_callback_input))
            blocks.append(SelectBlock(_MULTI_OCTAVE, 1, 2, 1, 4, selected_block == _MULTI_OCTAVE, 'octave', OCTAVE_OPTIONS,
                                      default_selection=3, callback_func=_callback_input))
            blocks.append(SelectBlock(_MULTI_SHIFT, 1, 3, 1, 4, selected_block == _MULTI_SHIFT, 'shift', OCTAVE_OPTIONS,
                                      callback_func=_callback_input))
            for i in range(_MULTIPAD_MAX):
                row, col = divmod(i, _MAX_MULTI_COLUMNS)
                blocks.append(SelectBlock(_MULTI_FIRST_PAD + i, 2 + row, col, 1, 4, selected_block == _MULTI_FIRST_PAD + i,
                                          callback_func=_callback_input))
            empty_blocks.append(EmptyBlock(5, 3, 1, 4))
        else: # sub_page == _SUB_PAGE_MULTI_CHORD
            title_bar = TitleBar('multipad: assign chords', 4, _SUB_PAGES)
            blocks.append(ButtonBlock(_MULTI_NOTE_UP, 0, 0, 1, 2, selected_block == _MULTI_NOTE_UP, 'note ' + _ICON_UP,
                                        callback_func=_callback_input))
            blocks.append(ButtonBlock(_MULTI_NOTE_DOWN, 0, 1, 1, 2, selected_block == _MULTI_NOTE_DOWN, 'note ' + _ICON_DOWN,
                                        callback_func=_callback_input))
            blocks.append(ButtonBlock(_MULTI_OCTAVE_UP, 1, 0, 1, 2, selected_block == _MULTI_OCTAVE_UP, 'octave ' + _ICON_UP,
                                        callback_func=_callback_input))
            blocks.append(ButtonBlock(_MULTI_OCTAVE_DOWN, 1, 1, 1, 2, selected_block == _MULTI_OCTAVE_DOWN, 'octave ' + _ICON_DOWN,
                                        callback_func=_callback_input))
            for i in range(_MULTIPAD_MAX):
                row, col = divmod(i, _MAX_MULTI_COLUMNS)
                blocks.append(TextBlock(_MULTI_CHORD_FIRST + i, 2 + row, col, 1, 4, selected_block == _MULTI_CHORD_FIRST + i,
                                        callback_func=_callback_input))
            empty_blocks.append(EmptyBlock(5, 3, 1, 4))
        text_row = TextRow(_TEXT_ROW_Y, _TEXT_ROW_H, _BACK_COLOR, _FORE_COLOR, _ALIGN_CENTRE)
        return title_bar, blocks, empty_blocks, text_row

    def _load(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks; called by self.set_visibility, Page*.program_change, Page*.process_user_input
        and PageProgram.set_trigger'''
        redraw &= ml.ui.active_pop_up is None
        self._set_toms_options()
        self._set_multi_options()
        if redraw:
            self._set_text_row(redraw=False)
            self.draw()

    def _set_sub_page(self, sub_page: int) -> None:
        '''set sub-page to be visible; called by Page*.process_user_input and Page*._build_page'''
        if sub_page == _SUB_PAGE_TOMS:
            self._initiate_toms()
        else:
            self._initiate_multipad()
        super()._set_sub_page(sub_page)

    def _set_text_row(self, value: int|None = None, redraw: bool = True) -> None:
        '''draw text row with long description of currently selected block; called by self.encoder and self._load'''
        selection = self.selected_block[(sub_page := self.sub_page)]
        if sub_page == _SUB_PAGE_TOMS:
            text = TEXT_ROWS_TOOLS[_SUB_PAGE_TOMS][selection]
        elif sub_page == _SUB_PAGE_MULTIPAD:
            if selection < _MULTIPAD_FIRST_MODE:
                text = TEXT_ROWS_TOOLS[_SUB_PAGE_MULTIPAD][selection]
            else:
                text = TEXT_ROWS_TOOLS[_SUB_PAGE_MULTIPAD][_MULTIPAD_FIRST_MODE]
        elif sub_page == _SUB_PAGE_MULTI_NOTE:
            if selection == _MULTI_PATTERN:
                pattern = self.multi_pattern if value is None else value
                text = PATTERN_OPTIONS[1][pattern]
            elif selection < _MULTI_FIRST_PAD:
                text = TEXT_ROWS_TOOLS[_SUB_PAGE_MULTI_NOTE][selection]
            else:
                row, col = divmod(selection - _MULTI_FIRST_PAD, _MAX_MULTI_COLUMNS)
                n = MULTI_LAYOUTS[self.multi_layout * _LAYOUT_COLS + _LAYOUT_MAP_COL][row][col] # type: ignore
                text = '' if n == _NONE else f'set note for pad {n + 1}' # type: ignore
        else: # sub_page == _SUB_PAGE_MULTI_CHORD
            if selection < _MULTI_CHORD_FIRST:
                text = TEXT_ROWS_TOOLS[_SUB_PAGE_MULTI_CHORD][selection]
            else:
                row, col = divmod(selection - _MULTI_CHORD_FIRST, _MAX_MULTI_COLUMNS)
                n = MULTI_LAYOUTS[self.multi_layout * _LAYOUT_COLS + _LAYOUT_MAP_COL][row][col] # type: ignore
                text = '' if n == _NONE else f'set chord for pad {n + 1}' # type: ignore
        self.text_row.set_text(text, redraw) # type: ignore

    def _set_toms_options(self) -> None:
        '''load and set options and values to input blocks on the batch assign toms sub-page; called by self.process_user_input and
        self._load'''
        if self.sub_page != _SUB_PAGE_TOMS:
            return
        if not self.toms_initiated:
            self._initiate_toms()
        blocks = self.blocks
        blocks[_TOMS_ZONE].set_options(selection=self.toms_zone, redraw=False)
        if (n := self.nr_toms - _MIN_TOMS) < 0:
            intervals = EMPTY_OPTIONS_4
            chords = EMPTY_OPTIONS_4
        else:
            intervals = GenOptions(len(TOMS_INTERVALS[n]) // 2 + 1, first_options=EMPTY_OPTIONS_4,
                                   func=lambda i: TOMS_INTERVALS[self.nr_toms - _MIN_TOMS][2 * i])
            chords = GenOptions(len(TOMS_CHORDS[n]) // 2 + 1, first_options=EMPTY_OPTIONS_4,
                                func=lambda i: TOMS_CHORDS[self.nr_toms - _MIN_TOMS][2 * i])
        blocks[_TOMS_INTERVAL].set_options(intervals, self.toms_interval + 1, redraw=False) # _NONE becomes 0
        blocks[_TOMS_CHORD].set_options(chords, self.toms_chord + 1, redraw=False) # _NONE becomes 0
        blocks[_TOMS_NOTE].set_options(selection=self.toms_note + 1, redraw=False) # _NONE becomes 0
        blocks[_TOMS_OCTAVE].set_options(selection=self.toms_octave + 2, redraw=False) # _OCTAVE_NONE becomes 0
        nr_tom_triggers = self.nr_tom_triggers
        for i, setting in enumerate(self.toms_settings):
            block = blocks[_TOMS_FIRST_CHECK + _MAX_TOMS - i - 1] # reverse order because the typical tom setup is from high to low
            block.enable(i < nr_tom_triggers, redraw=False)
            block.set_checked((checked := setting[_TOMS_CHECKED_COL]), False)
            block = blocks[_TOMS_FIRST_NOTE + _MAX_TOMS - i - 1] # reverse order because the typical tom setup is from high to low
            block.enable(checked, redraw=False)
            if checked:
                block.set_options(NOTE_OPTIONS, setting[_TOMS_NOTE_COL] + 1, 0, False) # _NONE becomes 0
            else:
                block.set_options((), redraw=False)

    def _set_multi_options(self) -> None:
        '''load and set options and values to input blocks on the batch assign toms sub-page; called by self._load'''
        sub_page = self.sub_page
        if sub_page != _SUB_PAGE_MULTIPAD and sub_page != _SUB_PAGE_MULTI_NOTE and sub_page !=_SUB_PAGE_MULTI_CHORD:
            return
        if not self.multi_initiated:
            self._initiate_multipad()
        settings = self.multi_settings
        layout = self.multi_layout
        layouts = MULTI_LAYOUTS
        map = layouts[layout * _LAYOUT_COLS + _LAYOUT_MAP_COL]
        rows = MULTI_LAYOUTS[layout * _LAYOUT_COLS + _LAYOUT_ROWS_COL]
        cols = MULTI_LAYOUTS[layout * _LAYOUT_COLS + _LAYOUT_COLS_COL]
        blocks = self.blocks
        if sub_page == _SUB_PAGE_MULTIPAD:
            blocks[_MULTIPAD_ZONE].set_options(selection=self.multi_zone, redraw=False)
            for row, row_map in enumerate(map): # type: ignore
                n = row * _LAYOUT_MAP_COLS
                for col, pad in enumerate(row_map):
                    if (i := n + col) >= _MULTIPAD_MAX:
                        continue
                    block = blocks[_MULTIPAD_FIRST_MODE + i]
                    block.set_row_dimentions(cols_per_row=cols)
                    if pad == _NONE:
                        block.set_options((), redraw=False)
                        block.set_label('', False)
                        block.enable(False, row < rows, col >= cols, False) # type: ignore
                    else:
                        block.set_options(MODE_OPTIONS, settings[row][col][_MULTI_MODE_COL], _MODE_OFF, False)
                        block.set_label(f'pad {pad + 1}', False)
                        block.enable(True, row < rows, col >= cols, False) # type: ignore
        elif sub_page == _SUB_PAGE_MULTI_NOTE:
            blocks[_MULTI_LAYER].set_options(selection=self.multi_voice_layer, redraw=False)
            blocks[_MULTI_SCALE].set_options(selection=(scale := self.multi_scale) + 1, redraw=False) # _NONE becomes 0
            blocks[_MULTI_PATTERN].set_options(selection=self.multi_pattern, redraw=False)
            block = blocks[_MULTI_KEY]
            block.set_options(selection=self.multi_key + 1, redraw=False) # _NONE becomes 0
            block = blocks[_MULTI_OCTAVE]
            block.set_options(selection=self.multi_octave + 2, redraw=False) # _OCTAVE_NONE becomes 0
            self.middle_shift = (middle_shift := abs(-(len_series := len(MULTI_SCALES[2 * scale + 1])) // 2) - 1)
            block = blocks[_MULTI_SHIFT]
            block.set_options(GenOptions(len_series, -len_series // 2 + 1, func=str), self.multi_shift + middle_shift, middle_shift, False)
            for i in range(_MULTIPAD_MAX):
                block = blocks[_MULTI_FIRST_PAD + i]
                block.set_row_dimentions(cols_per_row=cols)
                row, col = divmod(i, _LAYOUT_MAP_COLS)
                if (pad := map[row][col]) == _NONE: # type: ignore
                    block.set_options((), redraw=False)
                    block.set_label('', False)
                    block.enable(False, row < rows, col >= cols, False) # type: ignore
                else:
                    setting = settings[row][col]
                    if setting[_MULTI_MODE_COL] == _MODE_NOTE:
                        block.set_options(NOTE_OPTIONS, setting[_MULTI_VALUE_COL] + 1, 0, False) # _NONE becomes 0
                        enable = True
                    else:
                        block.set_options((), redraw=False)
                        enable = False
                    block.set_label(f'pad {pad + 1}') # type: ignore
                    block.enable(enable, row < rows, col >= cols, False) # type: ignore
        else: # sub_page == _SUB_PAGE_MULTI_CHORD
            for i in range(_MULTIPAD_MAX):
                block = blocks[_MULTI_CHORD_FIRST + i]
                row, col = divmod(i, _LAYOUT_MAP_COLS)
                block.set_row_dimentions(cols_per_row=cols)
                if (pad := map[row][col]) == _NONE: # type: ignore
                    block.set_value('', False)
                    block.set_label('', False)
                    block.enable(False, row < rows, col >= cols, False) # type: ignore
                else:
                    setting = settings[row][col]
                    if setting[_MULTI_MODE_COL] == _MODE_CHORD:
                        if type(chord := setting[_MULTI_VALUE_COL]) is list:
                            note_name = KEY_OPTIONS[chord[_CHORD_ROOT] + 1]
                            quality_name = QUALITY_OPTIONS_SHORT[(quality := chord[_CHORD_QUALITY]) + 1]
                            if (inversion := chord[_CHORD_INVERSION]) == 0:
                                inversion_name = ''
                            else:
                                inversion_name = f'{NOTE_OPTIONS[MULTI_CHORDS[quality * _MULTI_CHORD_COLUMNS + 2][inversion] % 12 + 1]}'
                            text = '___' if (octave := chord[_CHORD_OCTAVE]) == _OCTAVE_NONE else \
                                f'{note_name}{quality_name}{inversion_name}[{octave}]'
                        else:
                            text = '___'
                        block.set_value(text, False)
                        enable = True
                    else:
                        block.set_value('', False)
                        enable = False
                    block.enable(enable, row < rows, col >= cols, False) # type: ignore
                    block.set_label(f'pad {pad + 1}') # type: ignore
        self.empty_blocks[0].enable(False, rows > 2, cols <= 3, False) # type: ignore

    def _save_toms_settings(self) -> bool:
        '''save values from input blocks on the batch assign toms sub-page; called by self.process_user_input'''

        def set_layers(source_layers: dict, destination_layers: dict, note: int) -> bool:
            changed = False
            for key in list(destination_layers):
                if key not in source_layers:
                    del destination_layers[key]
                    changed = True
            for layer_key, source_layer in source_layers.items():
                if layer_key not in destination_layers:
                    destination_layer = source_layer.copy()
                    destination_layer['note'] = note
                    destination_layers[layer_key] = destination_layer
                    changed = True
                    continue                    
                destination_layer = destination_layers[layer_key]
                for key, source_item in source_layer.items():
                    if key == 'note':
                        if note != destination_layer['note']:
                            destination_layer['note'] = note
                            changed = True
                        continue
                    if source_item != destination_layer[key]:
                        destination_layer[key] = source_item
                        changed = True
            return changed

        if (base_tom := self.base_tom) == _NONE:
            return False
        _router = ml.router
        _router.handshake() # request second thread to wait
        settings = self.toms_settings
        routing = _router.routing
        triggers_short = TRIGGERS_SHORT
        layers = settings[base_tom][_TOMS_ROUTE_COL]['layers']
        selected_block = self.selected_block[self.sub_page]
        changed = False
        for setting in settings:
            if not setting[_TOMS_CHECKED_COL]:
                changed |= _TOMS_FIRST_CHECK <= selected_block < _TOMS_FIRST_NOTE
                continue
            if (route := setting[_TOMS_ROUTE_COL]) is None:
                new_layers = {}
                for key, value in layers.items():
                    new_layers[key] = value.copy()
                for layer in new_layers.values():
                    layer['note'] = setting[_TOMS_NOTE_COL]
                new_route = {'trigger': triggers_short[setting[_TOMS_TRIGGER_COL]], 'zone': self.toms_zone, 'layers': new_layers}
                setting[_TOMS_ROUTE_COL] = new_route
                routing.append(new_route)
                changed = True
            elif set_layers(layers, route['layers'], setting[_TOMS_NOTE_COL]):
                changed = True
        if changed:
            if not _router.program_changed:
                _router.program_changed = True
            _router.update(already_waiting=True)
        else:
            _router.resume() # resume second thread
        return changed

    def _save_multi_settings(self) -> bool:
        '''save values from input blocks on the batch multipad sub-pages; called by self.process_user_input'''

        def extract_layers(layers: dict, layer: int) -> dict:
            if layer == _LAYER_ALL:
                new_layers = {}
                for key, value in layers.items():
                    new_layers[key] = value.copy()
                return new_layers
            transient_layer = _TRANSIENT_LAYER_LOW if layer == _LAYER_LOW else _TRANSIENT_LAYER_HIGH
            new_layers = {}
            for key, value in layers.items():
                if value['transient'] == _NONE:
                    new_layers[key] = value
                else:
                    if value['transient_layer'] == transient_layer:
                        new_layers[key] = value
            return new_layers

        def merge_layers(source_layers: dict, destination_layers: dict, note_or_notes: int|list, layer: int = _LAYER_ALL) -> bool:
            is_list = type(note_or_notes) is list
            transient_layer = _TRANSIENT_LAYER_LOW if layer == _LAYER_LOW else _TRANSIENT_LAYER_HIGH
            changed = False
            for layer_key in list(destination_layers):
                if layer_key in source_layers:
                    if is_list and ord(layer_key) - _ASCII_A >= len(note_or_notes):
                        del destination_layers[layer_key]
                        changed = True
                else: # layer_key not in source_layers
                    if is_list or layer == _LAYER_ALL or destination_layers[layer_key]['transient_layer'] == transient_layer:
                        del destination_layers[layer_key]
                        changed = True
            if is_list:
                if len(source_layers) == 0:
                    return changed
                for i in range(_ASCII_A, _ASCII_A + 4):
                    if (key := chr(i)) in source_layers:
                        source_layer = source_layers[key]
                        break
                for i, note in enumerate(note_or_notes):
                    if (layer_key := chr(_ASCII_A + i)) not in destination_layers:
                        destination_layer = source_layer.copy()
                        destination_layer['note'] = note
                        destination_layers[layer_key] = destination_layer
                        changed = True
                        continue                    
                    destination_layer = destination_layers[layer_key]
                    for key, item in source_layer.items():
                        if key == 'note':
                            if destination_layer['note'] != note:
                                destination_layer['note'] = note
                                changed = True
                        elif item != destination_layer[key]:
                            destination_layer[key] = item
                            changed = True
            else:
                for layer_key, source_layer in source_layers.items():
                    if layer_key not in destination_layers:
                        destination_layer = source_layer.copy()
                        destination_layer['note'] = note_or_notes
                        destination_layers[layer_key] = destination_layer
                        changed = True
                        continue                    
                    destination_layer = destination_layers[layer_key]
                    for key, item in source_layer.items():
                        if key == 'note':
                            if destination_layer['note'] != note_or_notes:
                                destination_layer['note'] = note_or_notes
                                changed = True
                        elif item != destination_layer[key]:
                            destination_layer[key] = item
                            changed = True
            return changed

        if (sub_page := self.sub_page) == _SUB_PAGE_MULTI_NOTE and \
                ((id := self.selected_block[sub_page]) == _MULTI_SCALE or id == _MULTI_KEY or id == _MULTI_OCTAVE) and \
                (self.multi_key == _NONE or self.multi_octave == _OCTAVE_NONE or self.multi_scale == _NONE):
            return False
        _router = ml.router
        _router.handshake() # request second thread to wait
        routing = _router.routing
        triggers_short = TRIGGERS_SHORT
        multi_voice_layer = self.multi_voice_layer
        settings = self.multi_settings
        if (base_multi_note := self.base_multi_note) == _NONE:
            layers_note = None
        else:
            row, col = divmod(base_multi_note, _LAYOUT_COLS)
            layers_note = extract_layers(settings[row][col][_MULTI_ROUTE_COL]['layers'], multi_voice_layer)
        if (base_multi_chord := self.base_multi_chord) != _NONE:
            row, col = divmod(base_multi_chord, _LAYOUT_COLS)
            layers_chord = settings[row][col][_MULTI_ROUTE_COL]['layers']
        elif base_multi_note != _NONE:
            row, col = divmod(base_multi_note, _LAYOUT_COLS)
            layers_chord = settings[row][col][_MULTI_ROUTE_COL]['layers']
        else:
            layers_chord = None
        multi_zone = self.multi_zone
        changed = False
        is_multipad = sub_page == _SUB_PAGE_MULTIPAD
        _note_from_number_and_octave = mt.note_from_number_and_octave
        for _row in settings:
            for setting in _row:
                if (mode := setting[_MULTI_MODE_COL]) == _MODE_OFF:
                    continue
                if mode == _MODE_NOTE and layers_note is not None:
                    if (note := setting[_MULTI_VALUE_COL]) is None:
                        note = _NONE
                    if (route := setting[_MULTI_ROUTE_COL]) is None:
                        if is_multipad and setting[_MULTI_VALUE_COL] == _NONE:
                            continue
                        new_layers_note = {}
                        for key, value in layers_note.items():
                            new_layers_note[key] = value.copy()
                        new_route = {'trigger': triggers_short[setting[_MULTI_TRIGGER_COL]], 'zone': multi_zone,
                                     'layers': new_layers_note}
                        setting[_MULTI_ROUTE_COL] = new_route
                        routing.append(new_route)
                        changed = True
                    elif merge_layers(layers_note, route['layers'], note, multi_voice_layer):
                        changed = True
                elif mode == _MODE_CHORD and layers_chord is not None:
                    if type(chord := setting[_MULTI_VALUE_COL]) is list:
                        notes = list(MULTI_CHORDS[chord[_CHORD_QUALITY] * _MULTI_CHORD_COLUMNS + 2])
                        base_note = _note_from_number_and_octave(chord[_CHORD_ROOT], chord[_CHORD_OCTAVE])
                        for i in range(len(notes)):
                            notes[i] += base_note
                        for i in range((inversion := chord[_CHORD_INVERSION]) - 1):
                            notes[i] += 12
                        if inversion > 0:
                            notes.sort()
                    else:
                        notes = [_NONE]
                    if (route := setting[_MULTI_ROUTE_COL]) is None:
                        new_route = {'trigger': triggers_short[setting[_MULTI_TRIGGER_COL]], 'zone': multi_zone, 'layers': {}}
                        setting[_MULTI_ROUTE_COL] = new_route
                        routing.append(new_route)
                        changed |= merge_layers(layers_chord, new_route['layers'], notes)
                    elif merge_layers(layers_chord, route['layers'], notes):
                        changed = True
        if changed:
            if not _router.program_changed:
                _router.program_changed = True
            _router.update(already_waiting=True)
        else:
            _router.resume() # resume second thread
        return changed

    def _initiate_toms(self) -> None:
        '''check toms mapping to construct initial batch toms assignment settings; called by self.program_change,
        self.process_user_input, self._set_sub_page and self._set_toms_options'''

        def compare_layers(layers_0: dict, layers_1: dict) -> bool:
            for layer_key, layer_0 in layers_0.items():
                if layer_key not in layers_1:
                    return False
                for key, item in layer_0.items():
                    if key == 'note':
                        continue
                    if item != layers_1[layer_key][key]:
                        return False
            return True

        _ml = ml
        _router = _ml.router
        if _router is None:
            return
        _router.handshake() # request second thread to wait
        for setting in (settings := self.toms_settings):
            setting[_TOMS_ROUTE_COL] = None
            setting[_TOMS_TRIGGER_COL] = _NONE
            setting[_TOMS_CHECKED_COL] = False
            setting[_TOMS_NOTE_COL] = _NONE
        # identify toms in trigger mapping and store number of tom triggers
        toms = []
        trigger_matrix = _router.trigger_matrix
        triggers_short = TRIGGERS_SHORT
        for i in range(_MATRIX_ROWS):
            for j in range(_MATRIX_COLUMNS):
                if (trigger := trigger_matrix[i][j]) == _NONE:
                    continue
                trigger_short = triggers_short[trigger]
                if trigger_short[0] == 'T':
                    toms.append(trigger)
        toms.sort(reverse=True)
        self.nr_tom_triggers = len(toms)
        # store triggers in toms_settings
        for i, trigger in enumerate(toms):
            settings[i][_TOMS_TRIGGER_COL] = trigger
        # store pointers to routes in toms_settings
        for route in _router.routing:
            if route['zone'] != self.toms_zone:
                continue
            trigger_short = route['trigger']
            if trigger_short[0] != 'T':
                continue
            setting = settings[toms.index(triggers_short.index(trigger_short))]
            if setting[_TOMS_ROUTE_COL] is None:
                setting[_TOMS_ROUTE_COL] = route
        # identify which toms have the most definitions in common and assume those are the included toms
        count = []
        for setting_0 in settings:
            if (route_0 := setting_0[_TOMS_ROUTE_COL]) is None:
                count.append(0)
                continue
            layers_0 = route_0['layers']
            n = 0
            for setting_1 in settings:
                if (route_1 := setting_1[_TOMS_ROUTE_COL]) is None:
                    continue
                n += int(compare_layers(layers_0, route_1['layers']))
            count.append(n)
        self.nr_toms = (max_count := max(count))
        # store reference to trigger used for copying definitions from
        if max_count == 0:
            self.base_tom = _NONE
        else:
            self.base_tom = (base_tom := count.index(max_count))
        # store checked status and note in toms_settings for identified ports
            source_layers = settings[base_tom][_TOMS_ROUTE_COL]['layers']
            for setting in settings:
                if (route := setting[_TOMS_ROUTE_COL]) is None:
                    continue
                if compare_layers(source_layers, (layers := route['layers'])):
                    setting[_TOMS_CHECKED_COL] = True
                    for i in range(_ASCII_A, _ASCII_A + 4):
                        if (key := chr(i)) in layers:
                            note = layers[key]['note']
                            break
                    setting[_TOMS_NOTE_COL] = note
        self._identify_toms_parameters()
        self.toms_initiated = True
        _router.resume() # resume second thread

    def _initiate_multipad(self) -> None:
        '''check multipad mapping to construct initial batch multipad assignment settings; called by self.program_change,
        self.process_user_input and self._set_sub_page'''

        def compare_layers(layers_0: dict, layers_1: dict, transient_layer: int = _LAYER_ALL) -> bool:
            for layer_key, layer_0 in layers_0.items():
                if transient_layer != _LAYER_ALL and layer_0['transient_layer'] != transient_layer:
                    continue
                if layer_key not in layers_1:
                    return False
                for key, item in layer_0.items():
                    if key == 'note':
                        continue
                    if item != layers_1[layer_key][key]:
                        return False
            return True

        _ml = ml
        if (_router := _ml.router) is None:
            return
        _router.handshake() # request second thread to wait
        if self.multi_initiated:
            self._identify_multi_parameters()
            _router.resume() # resume second thread
            return
        for _row in (settings := self.multi_settings):
            for setting in _row:
                setting[_MULTI_ROUTE_COL] = None
                setting[_MULTI_TRIGGER_COL] = _NONE
                setting[_MULTI_VALUE_COL] = None
        # identify pads in trigger mapping, determine number of rows and columns and identify layout
        first_row = _MAX_MULTI_ROWS
        last_row = _NONE
        first_col = _MAX_MULTI_COLUMNS
        last_col = 0
        trigger_matrix = _router.trigger_matrix
        triggers_short = TRIGGERS_SHORT
        for i in range(_MATRIX_ROWS):
            for j in range(_MATRIX_COLUMNS):
                if (trigger := trigger_matrix[i][j]) == _NONE:
                    continue
                if triggers_short[trigger][0] == 'M':
                    first_row = min(i, first_row)
                    last_row = max(i, last_row)
                    first_col = min(j, first_col)
                    last_col = max(j, last_col)
        layout = _DEFAULT_LAYOUT
        layouts = MULTI_LAYOUTS
        if last_row == _NONE:
            rows = 2
            cols = 4
        else:
            rows = last_row - first_row + 1
            cols = last_col - first_col + 1
            for i in range(len(layouts) // _LAYOUT_COLS):
                layout_pos = _LAYOUT_COLS * i
                if layouts[layout_pos + _LAYOUT_ROWS_COL] != rows or layouts[layout_pos + _LAYOUT_COLS_COL] != cols:
                    continue
                match = True
                for row in range(rows):
                    for col in range(cols):
                        if trigger_matrix[first_row + row][first_col + col] - _FIRST_PAD != \
                                layouts[layout_pos + _LAYOUT_MAP_COL][row][col]: # type: ignore
                            match = False
                            break
                    if not match:
                        break
                if match:
                    layout = i
                    break
        self.multi_layout = layout
        # store triggers in multi_settings
        first_pad = TRIGGERS_SHORT.index('M1')
        for layout_row, row_map in enumerate(map := layouts[layout * _LAYOUT_COLS + _LAYOUT_MAP_COL]): # type: ignore
            for layout_col, pad in enumerate(row_map):
                if pad != _NONE:
                    settings[layout_row][layout_col][_MULTI_TRIGGER_COL] = first_pad + pad
        # store pointers to routes in multi_settings
        multi_zone = self.multi_zone
        for route in _router.routing:
            if route['zone'] != multi_zone:
                continue
            trigger_short = route['trigger']
            if trigger_short[0] != 'M':
                continue
            pad_route = int(trigger_short[1:], 16) - 1
            for layout_row, row_map in enumerate(map): # type: ignore
                for layout_col, pad_layout in enumerate(row_map):
                    if pad_layout == pad_route:
                        settings[layout_row][layout_col][_MULTI_ROUTE_COL] = route
                        break
        # identify which pads are potenially assigned to notes and to chords
        for _row in settings:
            for setting in _row:
                if (route := setting[_MULTI_ROUTE_COL]) is None:
                    continue
                n_layer = 0
                n_layer_low = 0
                n_layer_high = 0
                all_same_note = True
                all_same_note_low = True
                all_same_note_high = True
                for i in range(_ASCII_A, _ASCII_A + 4):
                    if (key := chr(i)) not in (layers := route['layers']):
                        continue
                    layer = layers[key]
                    n_layer += 1
                    if n_layer == 1:
                        first_note = layer['note']
                    else:
                        if layer['note'] != first_note:
                            all_same_note = False
                    if layer['transient_layer'] == _LAYER_LOW:
                        n_layer_low += 1
                        if n_layer_low == 1:
                            first_note_low = layer['note']
                        else:
                            if layer['note'] != first_note_low:
                                all_same_note_low = False
                    elif layer['transient_layer'] == _LAYER_HIGH:
                        n_layer_high += 1
                        if n_layer_high == 1:
                            first_note_high = layer['note']
                        else:
                            if layer['note'] != first_note_high:
                                all_same_note_high = False
                if n_layer > 0:
                    if all_same_note or all_same_note_low and all_same_note_high and n_layer == n_layer_low + n_layer_high:
                        setting[_MULTI_MODE_COL] = _MODE_NOTE
                    elif n_layer > 1:
                        setting[_MULTI_MODE_COL] = _MODE_CHORD
        # identify which have the most definitions in common and assume those are the included ones
        count_note = []
        count_chord = []
        multi_voice_layer = self.multi_voice_layer
        for settings_col_0 in settings:
            for setting_0 in settings_col_0:
                route_0 = setting_0[_MULTI_ROUTE_COL]
                if (mode := setting_0[_MULTI_MODE_COL]) == _MODE_OFF or route_0 is None:
                    count_note.append(0)
                    count_chord.append(0)
                    continue
                route_0 = setting_0[_MULTI_ROUTE_COL]
                layers_0 = route_0['layers']
                if mode == _MODE_NOTE:
                    n = 0
                    for settings_col_1 in settings:
                        for setting_1 in settings_col_1:
                            if (route_1 := setting_1[_MULTI_ROUTE_COL]) is None or setting_1[_MULTI_MODE_COL] != _MODE_NOTE:
                                continue
                            n += int(compare_layers(layers_0, route_1['layers'], multi_voice_layer))
                    count_note.append(n)
                    count_chord.append(0)
                elif mode == _MODE_CHORD:
                    n = 0
                    for settings_col_1 in settings:
                        for setting_1 in settings_col_1:
                            if (route_1 := setting_1[_MULTI_ROUTE_COL]) is None or setting_1[_MULTI_MODE_COL] != _MODE_CHORD:
                                continue
                            n += int(compare_layers(layers_0, route_1['layers']))
                        count_note.append(0)
                        count_chord.append(n)
        # store reference to triggers used for copying definitions from
        base_multi_note = _NONE if (max_note := max(count_note)) == 0 else count_note.index(max_note)
        self.base_multi_note = base_multi_note
        base_multi_chord = _NONE if (max_chord := max(count_chord)) == 0 else (base_multi_chord := count_chord.index(max_chord))
        self.base_multi_chord = base_multi_chord
        # update pad modes and notes in multi_settings for identified ports
        if base_multi_note != _NONE:
            row, col = divmod(base_multi_note, _LAYOUT_COLS)
            if (source_route := settings[row][col][_MULTI_ROUTE_COL]) is not None:
                source_layers = source_route['layers']
                for _row in settings:
                    for setting in _row:
                        if setting[_MULTI_MODE_COL] != _MODE_NOTE:
                            continue
                        if (route := setting[_MULTI_ROUTE_COL]) is None:
                            if setting[_MULTI_VALUE_COL] is None:
                                setting[_MULTI_VALUE_COL] = _NONE
                            continue
                        if (key := chr(_ASCII_A + multi_voice_layer)) in (layers := route['layers']):
                            setting[_MULTI_VALUE_COL] = layers[key]['note']
                        else:
                            setting[_MULTI_VALUE_COL] = _NONE
        if base_multi_chord != _NONE:
            row, col = divmod(base_multi_chord, _LAYOUT_COLS)
            if (source_route := settings[row][col][_MULTI_ROUTE_COL]) is not None:
                source_layers = source_route['layers']
                for _row in settings:
                    for setting in _row:
                        if (route := setting[_MULTI_ROUTE_COL]) is None or setting[_MULTI_MODE_COL] != _MODE_CHORD:
                            continue
                        if compare_layers(source_layers, (layers := route['layers']), multi_voice_layer):
                            chord = []
                            for layer in layers.values():
                                if (note := layer['note']) != _NONE:
                                    chord.append(note)
                            chord.sort()
                            if not (chord_def := setting[_MULTI_VALUE_COL]) is list:
                                chord_def = [_NONE, _OCTAVE_NONE, _NONE, 0]
                                setting[_MULTI_VALUE_COL] = chord_def
                            _mt = mt
                            if (len_chord := len(chord)) > 0:
                                first_note = chord[0]
                                series = []
                                for note in chord:
                                    series.append(note - first_note)
                            match = False
                            for inversion in range(len(chord)):
                                for quality in range(len(MULTI_CHORDS) // _MULTI_CHORD_COLUMNS):
                                    if len(ref_series := MULTI_CHORDS[quality * _MULTI_CHORD_COLUMNS + 2]) != len_chord:
                                        continue
                                    if inversion > 0:
                                        ref_series = list(ref_series)
                                        for i in range(inversion - 1):
                                            ref_series[i] += 12 # type: ignore
                                        ref_series.sort()
                                    found = True
                                    for i, note in enumerate(ref_series):
                                        if series[i] != note:
                                            found = False
                                    if found:
                                        match = True
                                        break
                                if match:
                                    break
                            if match:
                                root = _mt.number_to_base_note(base_note := chord[inversion])
                                octave = _mt.number_to_octave(base_note)
                            else:
                                root = _NONE
                                octave = _OCTAVE_NONE
                                quality = _NONE
                                inversion = 0
                            chord_def[_CHORD_ROOT] = root # type: ignore
                            chord_def[_CHORD_OCTAVE] = octave # type: ignore
                            chord_def[_CHORD_QUALITY] = quality # type: ignore
                            chord_def[_CHORD_INVERSION] = inversion # type: ignore
        self._identify_multi_parameters()
        self.multi_initiated = True
        _router.resume() # resume second thread

    def _identify_toms_parameters(self) -> None:
        '''identify toms parameters based on set notes; called by self.midi_learn, self.process_user_input and self._initiate_toms'''
        if self.base_tom == _NONE:
            self.toms_note = _NONE
            self.toms_octave = _OCTAVE_NONE
            return
        # identify lowest note and count number of toms
        lowest_note = 128 # 1 higher than the highest possible MIDI note number
        nr_toms = 0
        for setting in (settings := self.toms_settings):
            if setting[_TOMS_CHECKED_COL]:
                nr_toms += 1
                if (note := setting[_TOMS_NOTE_COL]) < lowest_note:
                    lowest_note = note
        self.nr_toms = nr_toms
        # identify lowest note and octave
        _mt = mt
        note = _NONE if lowest_note == 128 else _mt.number_to_base_note(lowest_note)
        self.toms_note = note
        if note == _NONE:
            self.toms_octave = _OCTAVE_NONE
            return
        self.toms_octave = _mt.number_to_octave(lowest_note)
        # identify interval or chord
        spacing = [setting[_TOMS_NOTE_COL] - lowest_note for setting in settings if setting[_TOMS_CHECKED_COL]]
        spacing = tuple(spacing)
        self.toms_interval = _NONE
        self.toms_chord = _NONE
        n = nr_toms - _MIN_TOMS
        if len(intervals := TOMS_INTERVALS) > n >= 0:
            intervals = intervals[n]
            for i in range(len(intervals) // 2):
                if intervals[2 * i + 1] == spacing:
                    self.toms_interval = i
                    break
        if len(chords := TOMS_CHORDS) > n >= 0:
            chords = chords[n]
            for i in range(len(chords) // 2):
                if chords[2 * i + 1] == spacing:
                    self.toms_chord = i
                    break

    def _identify_multi_parameters(self) -> None:
        '''identify mutli parameters based on set notes; called by self.midi_learn, self.process_user_input and self._initiate_multipad'''
        if self.base_multi_note == _NONE:
            self.multi_scale = _NONE
            self.multi_pattern = _PATTERN_NONE
            self.multi_key = _NONE
            self.multi_octave = _OCTAVE_NONE
            self.multi_shift = 0
            return
        # identify pattern for scales/modes assigned to pads (notes)
        pattern = _PATTERN_NONE
        previous = _NONE
        fail = False
        for _row in reversed(settings := self.multi_settings):
            for setting in _row:
                if setting[_MULTI_MODE_COL] != _MODE_NOTE:
                    continue
                if (note := setting[_MULTI_VALUE_COL]) == _NONE:
                    continue
                if note <= previous:
                    fail = True
                    break
                previous = note
            if fail:
                break
        layouts = MULTI_LAYOUTS
        if fail:
            rows = layouts[(layout_pos := _LAYOUT_COLS * self.multi_layout) + _LAYOUT_ROWS_COL]
            cols = layouts[layout_pos + _LAYOUT_COLS_COL]
            previous = _NONE
            fail = False
            for col in range(cols): # type: ignore
                for row in range(rows - 1, -1, -1): # type: ignore
                    setting = settings[row][col]
                    if setting[_MULTI_MODE_COL] != _MODE_NOTE:
                        continue
                    if (note := setting[_MULTI_VALUE_COL]) == _NONE:
                        continue
                    if note <= previous:
                        fail = True
                        break
                    previous = note
                if fail:
                    break
            if not fail:
                pattern = _PATTERN_UP_RIGHT
        else:
            pattern = _PATTERN_RIGHT_UP
        self.multi_pattern = pattern
        # identify key, octave, scale/mode and shift
        if pattern == _PATTERN_RIGHT_UP:
            notes = [note for row in reversed(settings) for setting in row \
                     if setting[_MULTI_MODE_COL] == _MODE_NOTE and (note := setting[_MULTI_VALUE_COL]) != _NONE]
        else: # pattern == _PATTERN_UP_RIGHT
            notes = []
            for col in range(cols): # type: ignore
                for row in range(rows - 1, -1, -1): # type: ignore
                    setting = settings[row][col]
                    if setting[_MULTI_MODE_COL] == _MODE_NOTE and (note := setting[_MULTI_VALUE_COL]) != _NONE:
                        notes.append(note)
        if len(notes) == 0:
            self.multi_key = _NONE
            self.multi_octave = _OCTAVE_NONE
            self.multi_shift = 0
            return
        scales = MULTI_SCALES
        nr_pads = sum([1 for _row in settings for setting in _row if setting[_MULTI_MODE_COL] == _MODE_NOTE])
        _mt = mt
        match = False
        for i in range(_MAX_SCALE_LENGTH):
            for scale in range(len(scales) // 2):
                if i >= len(scales[2 * scale + 1]):
                    continue
                shift = (1 - 2 * ((j := i + 1) % 2)) * (j // 2)
                shifted_series = self._shift_series(scales[2 * scale + 1], shift, nr_pads)
                base_note = notes[0] - shifted_series[0]
                match = True
                for j, note in enumerate(notes):
                    if note != base_note + shifted_series[j]:
                        match = False
                        break
                if match:
                    self.multi_scale = scale
                    self.multi_key = _mt.number_to_base_note(base_note)
                    self.multi_octave = _mt.number_to_octave(base_note)
                    self.multi_shift = shift
                    break
            if match:
                break
        if not match:
            self.multi_key = _NONE
            self.multi_octave = _OCTAVE_NONE
            self.multi_shift = 0

    def _set_toms_base_note(self, input_id: int, value: int) -> bool:
        '''adjust toms notes based on base note and octave setting; called by self.process_user_input and self.midi_learn'''
        if self.toms_interval == _NONE and self.toms_chord == _NONE:
            lowest_note = 128 # 1 higher than the highest possible MIDI note number
            for setting in (settings := self.toms_settings):
                if setting[_TOMS_CHECKED_COL]:
                    if (note := setting[_TOMS_NOTE_COL]) < lowest_note:
                        lowest_note = note
            if lowest_note != 128:
                if input_id == _TOMS_NOTE:
                    d = value - mt.number_to_base_note(lowest_note)
                else:
                    d = (value - mt.number_to_octave(lowest_note)) * 12
                for setting in settings:
                    note = setting[_TOMS_NOTE_COL]
                    if setting[_TOMS_CHECKED_COL] and note != _NONE:
                        note += d
                        setting[_TOMS_NOTE_COL] = _NONE if note < -1 or note > 127 else note
                reidentify = self.toms_note != _NONE and self.toms_octave != _OCTAVE_NONE and \
                    (self.toms_interval != _NONE or self.toms_chord != _NONE)
        else:
            if not (reidentify := self._set_toms_series()):
                if input_id == _TOMS_NOTE:
                    self.blocks[_TOMS_NOTE].draw()
                else:
                    self.blocks[_TOMS_OCTAVE].draw()
        return reidentify

    def _set_toms_series(self) -> bool:
        '''set toms notes to interval or chord series; called by self.process_user_input and self._set_toms_base_note'''
        note = self.toms_note
        octave = self.toms_octave
        interval = self.toms_interval
        chord = self.toms_chord
        if note == _NONE or octave == _OCTAVE_NONE or interval == _NONE and chord == _NONE:
            return False
        base_note = mt.note_from_number_and_octave(note, octave)
        if chord == _NONE:
            series = TOMS_INTERVALS[self.nr_toms - _MIN_TOMS][2 * interval + 1]
        else:
            series = TOMS_CHORDS[self.nr_toms - _MIN_TOMS][2 * chord + 1]
        i = 0
        for setting in self.toms_settings:
            if not setting[_TOMS_CHECKED_COL]:
                continue
            note = base_note + series[i] # type: ignore
            setting[_TOMS_NOTE_COL] = _NONE if note > 127 else note
            i += 1
        return True

    def _set_multi_key(self, input_id: int, value: int) -> bool:
        '''adjust multipad notes based on key and octave setting; called by self.process_user_input and self.midi_learn'''
        if (input_id == _MULTI_SCALE or input_id == _MULTI_KEY or input_id == _MULTI_OCTAVE) and \
                (self.multi_key == _NONE or self.multi_octave == _OCTAVE_NONE or self.multi_scale == _NONE):
            return False
        if self.multi_scale == _NONE:
            lowest_note = 128 # 1 higher than the highest possible MIDI note number
            for _row in (settings := self.multi_settings):
                for setting in _row:
                    if setting[_MULTI_MODE_COL] == _MODE_NOTE:
                        if (note := setting[_MULTI_VALUE_COL]) < lowest_note:
                            lowest_note = note
            if 0 <= lowest_note < 128:
                if input_id == _MULTI_KEY:
                    d = value - mt.number_to_base_note(lowest_note)
                else:
                    d = (value - mt.number_to_octave(lowest_note)) * 12
                for _row in settings:
                    for setting in _row:
                        if setting[_MULTI_MODE_COL] == _MODE_NOTE:
                            if (note := setting[_MULTI_VALUE_COL]) != _NONE:
                                note += d
                                setting[_MULTI_VALUE_COL] = note if -1 <= note <= 127 else _NONE
                reidentify = self.multi_key != _NONE and self.multi_octave != _OCTAVE_NONE and self.multi_scale != _NONE
            else:
                return False
        else:
            if not (reidentify := self._set_multi_series()):
                if input_id == _MULTI_KEY:
                    self.blocks[_MULTI_KEY].draw()
                else:
                    self.blocks[_MULTI_OCTAVE].draw()
        return reidentify

    def _set_multi_series(self) -> bool:
        '''set mutipad notes to scale/mode series; called by self.process_user_input and self._set_multi_key'''
        octave = self.multi_octave
        scale = self.multi_scale
        pattern = self.multi_pattern
        if (key := self.multi_key) == _NONE or octave == _OCTAVE_NONE or scale == _NONE or pattern == _PATTERN_NONE:
            return False
        base_note = mt.note_from_number_and_octave(key, octave)
        series = MULTI_SCALES[2 * scale + 1]
        settings = self.multi_settings
        nr_pads = sum([1 for _row in settings for setting in _row if setting[_MULTI_MODE_COL] == _MODE_NOTE])
        shifted_series = self._shift_series(series, self.multi_shift, nr_pads)
        i = -1
        if pattern == _PATTERN_RIGHT_UP:
            for _row in reversed(settings):
                for setting in _row:
                    if setting[_MULTI_MODE_COL] != _MODE_NOTE:
                        continue
                    i += 1
                    note = base_note + shifted_series[i]
                    setting[_MULTI_VALUE_COL] = _NONE if note > 127 else note
        else: # pattern == _PATTERN_UP_RIGHT
            layouts = MULTI_LAYOUTS
            rows = layouts[(layout_pos := _LAYOUT_COLS * self.multi_layout) + _LAYOUT_ROWS_COL]
            cols = layouts[layout_pos + _LAYOUT_COLS_COL]
            for col in range(cols): # type: ignore
                for row in range(rows - 1, -1, -1): # type: ignore
                    setting = settings[row][col]
                    if setting[_MULTI_MODE_COL] != _MODE_NOTE:
                        continue
                    i += 1
                    note = base_note + shifted_series[i]
                    setting[_MULTI_VALUE_COL] = _NONE if note > 127 else note
        return True

    def _shift_series(self, series, shift: int, nr_pads: int):
        '''shifts series to start with a different note than the base note; called by self._identify_multi_parameters and
        self._set_multi_series'''
        shifted_series = list(series)
        if shift > 0:
            shifted_series = [x - 12 for x in series[-shift:]] + shifted_series
        elif shift < 0:
            shifted_series = shifted_series[-shift:]
        n = 1
        while len(shifted_series) < nr_pads:
            shifted_series = shifted_series + [x + n * 12 for x in series]
            n += 1
        if nr_pads < len(shifted_series):
            shifted_series = shifted_series[:nr_pads]
        return shifted_series

    def _callback_chord(self, pad: int, root: int, octave: int, quality: int, inversion: int) -> None:
        '''callback for chord pop-up; called (passed on) by self.process_user_input'''
        row, col = divmod(pad, _MAX_MULTI_COLUMNS)
        setting = self.multi_settings[row][col]
        if type(chord := setting[_MULTI_VALUE_COL]) is list:
            chord = setting[_MULTI_VALUE_COL]
        else:
            chord = [_NONE, _OCTAVE_NONE, _NONE, 0]
            setting[_MULTI_VALUE_COL] = chord
        chord[_CHORD_ROOT] = root
        chord[_CHORD_OCTAVE] = octave
        chord[_CHORD_QUALITY] = quality
        chord[_CHORD_INVERSION] = inversion
        self._set_multi_options()
        self._save_multi_settings()
        self.draw()