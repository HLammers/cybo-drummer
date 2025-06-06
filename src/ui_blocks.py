''' UI building blocks library for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024-2025 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

import time

import main_loops as ml
from constants import EMPTY_OPTIONS_BLANK, TRIGGERS, TRIGGERS_SHORT, TRIGGERS_LONG, MULTI_CHORDS, \
    TRIGGER_OPTIONS_SHORT, TRIGGER_OPTIONS_LONG, KEY_OPTIONS, OCTAVE_OPTIONS, QUALITY_OPTIONS_LONG, INVERSION_OPTIONS

_VERSION                = '0.3.0'
_YEAR                   = const(2025)

_NONE                   = const(-1)
_OCTAVE_NONE            = const(-2)

_ASCII_A                = const(65)

_ENCODER_NAV            = const(0)
_ENCODER_VAL            = const(1)

_ALIGN_LEFT             = const(0)
_ALIGN_CENTRE           = const(1)
_ALIGN_RIGHT            = const(2)

_COLOR_TABS_DARK        = const(0xAA29) # 0x29AA dark purple blue
_COLOR_TABS_LIGHT       = const(0xD095) # 0x95D0 green
_COLOR_TITLE_BACK       = const(0x06ED) # 0xED06 orange
_COLOR_TITLE_FORE       = const(0xAA29) # 0x29AA dark purple blue
_COLOR_CELL_ACTIVE      = const(0x06ED) # 0xED06 orange
_COLOR_BLOCK_DARK       = const(0xAA29) # 0x29AA dark purple blue
_COLOR_BLOCK_LIGHT      = const(0xD9CD) # 0xCDD9 light purple grey
_COLOR_SELECTED_DARK    = const(0x8E33) # 0x338E dark sea green
_COLOR_SELECTED_LIGHT   = const(0xFD97) # 0x97FD light sea green
_COLOR_SELECTED_CHANGED = const(0x6CA0) # 0xA06C purple
_COLOR_LINE             = const(0x06ED) # 0xED06 orange
_COLOR_POP_UP_DARK      = const(0x8E33) # 0x338E dark sea green
_COLOR_POP_UP_LIGHT     = const(0xFD97) # 0x97FD light sea green
_COLOR_POP_UP_INACTIVE  = const(0xD9CD) # 0xCDD9 light purple grey

_MARGIN                 = const(3)
_MARGIN_LARGE           = const(10)
_TAB_H                  = const(26)
_SUB_PAGE_W             = const(204)
_TITLE_BAR_H            = const(14)
_PROGRAM_NUMBER_W       = const(25)
_CELL_W                 = const(22)
_CELL_H                 = const(14)
_CELL_MARGIN            = const(4)
_TEXT_ROW_H             = const(13)
_BLOCK_H                = const(25)
_LABEL_H                = const(10)
_POP_UP_LABEL_H         = const(14)
_VALUE_H                = const(15)
_BUTTON_MARGIN_X        = const(20)
_BUTTON_MARGIN_Y        = const(4)
_TRIGGER_W              = const(22)
_TRIGGER_H              = const(11)
_TEXT_H                 = const(15)
_CURSOR_H               = const(10)
_CHAR_W                 = const(13)
_CHAR_H                 = const(11)
_CONTROL_H              = const(16)
_SELECT_TRIGGER_W       = const(160)
_MENU_W                 = const(102)
_CONFIRM_W              = const(102)

_ICON_UNCHECKED         = chr(127) + chr(128)
_ICON_CHECKED           = chr(129) + chr(130)

_INPUT_CHARS            = '''ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#%^&*()_-+=[]\\{}|:;"',./<>?'''
_INPUT_CHARS_FILE       = '''ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#%^&()_-+=[]{};',.'''
_CHARACTER_COLUMNS      = const(13)
_TEXT_INPUT_SPACE_BAR   = 'space bar'
_TEXT_INPUT_MAX_LENGTH  = const(27)

_MATRIX_ROWS            = const(8)
_MATRIX_COLUMNS         = const(8)
_MULTI_CHORD_COLUMNS    = const(3)

_TRIGGER_ROW            = const(0)
_TRIGGER_COL            = const(1)
_TRIGGER_TRIGGER        = const(2)
_TRIGGER_ZONE           = const(3)

_CHORD_ROOT             = const(0)
_CHORD_OCTAVE           = const(1)
_CHORD_QUALITY          = const(2)
# _CHORD_INVERSION        = const(3)

class Block():
    '''base class for ui blocks'''

    def __init__(self, id: int, row: int, col: int, cols: int, cols_per_row: int, selected: bool, label: str,
                 add_line: bool = False) -> None:
        self.id = id
        self.col = col
        self.cols = cols
        self.cols_per_row = cols_per_row
        self.w = int(cols * (w := (_SUB_PAGE_W / cols_per_row)))
        self.x = int(col * w)
        self.y = _TITLE_BAR_H + row * _BLOCK_H
        self.h = _BLOCK_H
        self.selected = selected
        self.label = label
        self.add_line = add_line
        self.enabled = True
        self.visible = True
        self.totally_hidden = False

    def update(self, selected: bool, redraw: bool = True, encoder_id: int = _ENCODER_VAL) -> None:
        '''update block, set selection state and redraw if necessary; called by PopUp.open, PopUp.close, ui.process_user_input,
        Page.set_visibility, Page.restore, Page.set_page_encoders, Page.encoder, Page._draw, Page._sub_page_selector and
        Page*.program_change'''
        pass

    def draw(self) -> None:
        '''draw block; called by self.enable'''
        pass

    def enable(self, enable: bool, visible: bool = True, totally_hidden: bool = False, redraw: bool = True) -> None:
        '''set whether a block can be selected or not; called by Page*._set_*_options'''
        self.enabled = enable
        self.visible = visible
        self.totally_hidden = totally_hidden
        if redraw:
            self.draw()

    def set_row_dimentions(self, cols: int|None = None, cols_per_row: int|None = None):
        '''change number of columns and/or columns per row called by Page*._set_*_options'''
        if cols == None:
            cols = self.cols
        else:
            self.cols = cols
        if cols_per_row is None:
            cols_per_row = self.cols_per_row
        else:
            self.cols_per_row = cols_per_row
        self.w = (w := (_SUB_PAGE_W // cols_per_row) * cols)
        self.x = self.col * w
        
    def encoder(self, value: int) -> bool:
        '''process value encoder input at block level (ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by Pages.encoder and PagesTabs.encoder'''
        return False

    def button_sel_opt(self) -> bool:
        '''process select button press at block level; called by Page.button_sel_opt'''
        return False

    def button_del(self) -> bool:
        '''process backspace button press at block level; called by Page.button_del'''
        return False

class PageTabs(Block):
    '''class providing page tabs block for ui; initiated once by PagesTabs.__init__'''

    def __init__(self, x: int, y: int, w: int, h: int, options: list|tuple, selection: int = 0) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.options = options
        self.selection = selection
        self.selected = False

    def update(self, selected, redraw: bool = True):
        '''update block, set selection state and redraw if necessary; called by PageTab.set_page_encoders'''
        self.selected = selected
        if selected:
            ml.ui.encoder_val.set(self.selection, len(self.options) - 1)
        if redraw:
            self.draw()

    def draw(self):
        '''draw whole block or only value part of block; called by PagesTabs.update, PagesTabs.encoder and PagesTabs.draw'''
        if self.selected:
            back_color = _COLOR_SELECTED_DARK
            fore_color = _COLOR_SELECTED_LIGHT
        else:
            back_color = _COLOR_TABS_DARK
            fore_color = _COLOR_TABS_LIGHT
        selection = self.selection
        _display = ml.ui.display
        _rect = _display.rect
        _rect((x := self.x), (y := self.y), (w := self.w), self.h, back_color, True) # type: ignore (temporary)
        _text = _display.text_box
        yy = y
        for i, text in enumerate(self.options):
            if i == selection:
                _rect(x, yy, w, _TAB_H, fore_color, True) # type: ignore (temporary)
                color_1 = fore_color
                color_2 = back_color
            else:
                color_1 = back_color
                color_2 = fore_color
            _text(x, yy, w, _TAB_H, text, color_1, color_2, _ALIGN_CENTRE)
            yy += _TAB_H - 1

    def encoder(self, value: int) -> bool:
        '''process value encoder input at block level (ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by PagesTabs.encoder'''
        if not self.selected:
            return False
        self.selection = value
        self.draw()
        return True

class TitleBar(Block):
    '''class providing title bar block for ui pages; initiated by Page*._build_sub_page or Page*._build_page'''

    def __init__(self, title: str, page_number: int, number_of_pages: int) -> None:
        self.title = title
        self.page_number = page_number
        self.number_of_pages = number_of_pages
        self.selected = False
        self.w = _SUB_PAGE_W
        self.h = _TITLE_BAR_H

    def update(self, selected, redraw: bool = True):
        '''update block, set selection state and redraw if necessary; called by Page.set_page_encoders, Page._draw and
        Page._sub_page_selector'''
        self.selected = selected
        if selected:
            ml.ui.encoder_nav.set(self.page_number - 1, self.number_of_pages - 1)
        if redraw:
            self.draw()

    def draw(self):
        '''draw whole block or only value part of block; called by self.update, Page.restore and Page._draw'''
        if self.selected:
            back_color = _COLOR_SELECTED_LIGHT
            fore_color = _COLOR_SELECTED_DARK
        else:
            back_color = _COLOR_TITLE_BACK
            fore_color = _COLOR_TITLE_FORE
        _router = ml.router
        program = f'{chr(_ASCII_A + _router.active_bank)}{_router.active_program:0>2}'
        if _router.program_changed:
            program += '*'
        page = f'{self.page_number}/{self.number_of_pages}'
        _display = ml.ui.display
        _display.rect(0, 0, _SUB_PAGE_W, _TITLE_BAR_H, back_color, True) # type: ignore (temporary)
        _text = _display.text_box
        _text(_MARGIN, 0, _PROGRAM_NUMBER_W, _TITLE_BAR_H, program, back_color, fore_color, _ALIGN_LEFT)
        _text(_PROGRAM_NUMBER_W + _MARGIN, 0, _SUB_PAGE_W - 2 * _PROGRAM_NUMBER_W - 2 * _MARGIN, _TITLE_BAR_H, self.title,
              back_color, fore_color, _ALIGN_CENTRE,)
        _text(_SUB_PAGE_W - _PROGRAM_NUMBER_W - _MARGIN, 0, _PROGRAM_NUMBER_W, _TITLE_BAR_H, page, back_color, fore_color, _ALIGN_RIGHT)

class MatrixCell(Block):
    '''class providing matrix cell block for trigger overview; initiated by PageMatrix._build_sub_page'''

    def __init__(self, id: int, row: int, col: int, selected: bool, trigger: int = 0, text: str = '', callback_func=None) -> None:
        self.id = id
        self.x = col * (_CELL_W + _CELL_MARGIN)
        self.y = _TITLE_BAR_H + _CELL_MARGIN + row * (_CELL_H + _CELL_MARGIN)
        self.w = _CELL_W + _CELL_MARGIN if col < _MATRIX_COLUMNS - 1 else _CELL_W
        self.h = _CELL_H + _CELL_MARGIN if row < _MATRIX_ROWS - 1 else _CELL_H
        self.selected = selected
        self.trigger = trigger
        self.text = ''
        self._callback_func = callback_func
        self.enabled = True

    def update(self, selected: bool, redraw: bool = True, encoder_id: int = _ENCODER_VAL) -> None:
        '''update block, set selection state and redraw if necessary; called by PopUp.open, PopUp.close, ui.process_user_input,
        Page.set_visibility, Page.set_page_encoders, Page.encoder and PageMatrix.program_change and Page._draw'''
        self.selected = selected
        if redraw:
            self.draw()

    def draw(self, suppress_selected: bool = False) -> None:
        '''draw block; called by self.update, self.set_values, self.set_selection and Page._draw'''
        selected = self.selected and not suppress_selected
        active = self.trigger == ml.router.input_trigger
        if selected:
            color_dark = _COLOR_CELL_ACTIVE if active else _COLOR_SELECTED_DARK
            color_light = _COLOR_SELECTED_LIGHT
        else:
            color_dark = _COLOR_BLOCK_DARK
            color_light = _COLOR_CELL_ACTIVE if active else _COLOR_BLOCK_LIGHT
        x = self.x
        y = self.y
        w = self.w
        h = self.h
        _display = ml.ui.display
        _rect = _display.rect
        if selected:
            if w > _CELL_W:
                _rect(x + _CELL_W, y, w - _CELL_W, _CELL_H, _COLOR_BLOCK_DARK, True) # type: ignore (temporary)
            if h > _CELL_H:
                _rect(x, y + _CELL_H, w, h - _CELL_H, _COLOR_BLOCK_DARK, True) # type: ignore (temporary)
            w = _CELL_W
            h = _CELL_H
            color = color_light
        else:
            color = color_dark
        has_text = len(text := self.text) > 0
        _text = _display.text_box
        _rect(x, y, w, h, color, True) # type: ignore (temporary)
        if not selected:
            _rect(x, y, _CELL_W, _CELL_H, color_light, has_text) # type: ignore (temporary)
        if has_text:
            _text(x, y, _CELL_W, _CELL_H, text, color_light, color_dark, _ALIGN_CENTRE)
        elif selected:
            _rect(x + 1, y + 1, _CELL_W - 2, _CELL_H - 2, color_dark, True) # type: ignore (temporary)

    def set_values(self, trigger: int, text: str, redraw: bool = True) -> None:
        '''set active trigger and trigger/zone text; called by self.set_selection, PageMatrix.midi_learn
        and PagesProgram._set_matrix_options'''
        self.trigger = trigger
        self.text = text
        if redraw:
            self.draw()

    def button_sel_opt(self) -> bool:
        '''process select button press at block level; called by Page.button_sel_opt'''
        if not self.selected:
            return False
        if (_callback_func := self._callback_func) is not None:
            _callback_func(self.id, button_sel_opt=True)
        return True

    def button_del(self) -> bool:
        '''process backspace button press at block level; called by Page.button_del'''
        if not self.selected:
            return False
        if (_callback_func := self._callback_func) is not None:
            _callback_func(self.id, button_del=True)
        return True

class EmptyRow():
    '''class providing empty row for ui pages; initiated by Page*._build_sub_page'''

    def __init__(self, row: int = _NONE, y: int = _NONE, h: int = _NONE) -> None:
        self.y = _TITLE_BAR_H + row * _BLOCK_H if y == _NONE else y
        self.w = _SUB_PAGE_W
        self.h = _BLOCK_H if h == _NONE else h

    def draw(self) -> None:
        '''draw whole block or only value part of block; called by Page._draw and Page*._load'''
        ml.ui.display.rect(0, self.y, self.w, self.h, _COLOR_BLOCK_DARK, True) # type: ignore (temporary)

class EmptyBlock(Block):
    '''class providing empty block for ui pages; initiated by Page*._build_sub_page'''

    def __init__(self, row: int, col: int, cols: int, cols_per_row: int, add_line: bool = False) -> None:
        super().__init__(_NONE, row, col, cols, cols_per_row, False, '', add_line)

    def draw(self) -> None:
        '''draw whole block or only value part of block; called by Page._draw and Page*._load'''
        if self.totally_hidden:
            return
        if not self.visible:
            ml.ui.display.rect(self.x, self.y, self.w, _BLOCK_H, _COLOR_BLOCK_DARK, True) # type: ignore (temporary)
            return
        _rect = ml.ui.display.rect
        _rect((x := self.x), (y := self.y), (w := self.w), _LABEL_H, _COLOR_BLOCK_LIGHT, True) # type: ignore (temporary)
        y += _LABEL_H
        if self.add_line:
            _rect(x, y, w, _VALUE_H - 2, _COLOR_BLOCK_DARK, True) # type: ignore (temporary)
            y += _VALUE_H - 2
            _rect(x, y, w, 2, _COLOR_LINE, True) # type: ignore (temporary)
        else:
            _rect(x, y, w, _VALUE_H, _COLOR_BLOCK_DARK, True) # type: ignore (temporary)

class ButtonBlock(Block):
    '''class providing button block for ui pages; initiated by Page*._build_sub_page'''

    def __init__(self, id, row: int, col: int, cols: int, cols_per_row: int, selected: bool, label: str, add_line: bool = False,
                 callback_func=None) -> None:
        super().__init__(id, row, col, cols, cols_per_row, selected, label, add_line)
        self._callback_func = callback_func

    def update(self, selected: bool, redraw: bool = True, encoder_id: int = _ENCODER_VAL) -> None:
        '''update block, set selection state and redraw if necessary; called by PopUp.open, PopUp.close, ui.process_user_input,
        Page.set_visibility, Page.set_page_encoders, Page.encoder, Page*.program_change and Page._draw'''
        self.selected = selected
        if redraw:
            self.draw()

    def draw(self, suppress_selected: bool = False, pressed: bool = False, only_value: bool = False) -> None:
        '''draw whole block or only value part of block; called by self.update, self.button_sel_opt and Page._draw'''
        if self.totally_hidden:
            return
        if not self.visible:
            ml.ui.display.rect(self.x, self.y, self.w, _BLOCK_H, _COLOR_BLOCK_DARK, True) # type: ignore (temporary)
            return
        x = self.x
        y = self.y
        w = self.w
        if self.selected and not suppress_selected:
            color_dark = _COLOR_SELECTED_DARK
            color_light = _COLOR_SELECTED_LIGHT
        else:
            color_dark = _COLOR_BLOCK_DARK
            color_light = _COLOR_BLOCK_LIGHT
        _display = ml.ui.display
        _rect = _display.rect
        if only_value:
            yy = y + _LABEL_H
            _rect(x, yy, w, _VALUE_H, color_dark, True) # type: ignore (temporary)
        else:
            _rect(x, y, w, _LABEL_H, color_light, True) # type: ignore (temporary)
            _display.text_box(x, y, w, _LABEL_H, self.label, color_light, color_dark, _ALIGN_CENTRE)
            yy = y + _LABEL_H
            _rect(x, yy, w, _VALUE_H, color_dark, True) # type: ignore (temporary)
        yy += _BUTTON_MARGIN_Y
        margin_x = _BUTTON_MARGIN_X if w > 4 * _BUTTON_MARGIN_X else _MARGIN
        _rect(x + margin_x, yy, w - 2 * margin_x, _VALUE_H - 2 * _BUTTON_MARGIN_Y, color_light, False) # type: ignore (temporary)
        if not pressed:
            _rect(x + margin_x + 2, yy + 2, w - 2 * margin_x - 5, _VALUE_H - 2 * _BUTTON_MARGIN_Y - 5, color_light, True) # type: ignore (temporary)
        if self.add_line:
            _rect(x, y + _BLOCK_H - 2, w, 2, _COLOR_LINE, True) # type: ignore (temporary)

    def button_sel_opt(self) -> bool:
        '''process select button press at block level; called by Page.button_sel_opt'''
        if not self.selected:
            return False
        self.draw(pressed=True)
        time.sleep_ms(300)
        self.draw()
        if (_callback_func := self._callback_func) is not None:
            _callback_func(self.id, button_sel_opt=True)
        return True

class CheckBoxBlock(Block):
    '''class providing check box block for ui pages; initiated by Page*._build_sub_page'''

    def __init__(self, id, row: int, col: int, cols: int, cols_per_row: int, selected: bool, label: str = '', checked: bool = False,
                 default_selection: bool = False, add_line: bool = False, callback_func=None) -> None:
        super().__init__(id, row, col, cols, cols_per_row, selected, label, add_line)
        self.checked = checked
        self.default_selection = default_selection
        self._callback_func = callback_func

    def update(self, selected: bool, redraw: bool = True, encoder_id: int = _ENCODER_VAL) -> None:
        '''update block, set selection state and redraw if necessary; called by PopUp.open, PopUp.close, ui.process_user_input,
        Page.set_visibility, Page.set_page_encoders, Page.encoder and Page*.program_change and Page._draw'''
        self.selected = selected
        if selected:
            encoder = ml.ui.encoder_nav if encoder_id == _ENCODER_NAV else ml.ui.encoder_val
            encoder.set(0, 1)
        if redraw:
            self.draw()

    def draw(self, suppress_selected: bool = False, only_value: bool = False) -> None:
        '''draw whole block or only value part of block; called by self.update, self.set_label, self.set_checked and Page._draw'''
        if self.totally_hidden:
            return
        if not self.visible:
            ml.ui.display.rect(self.x, self.y, self.w, _BLOCK_H, _COLOR_BLOCK_DARK)
            return
        x = self.x
        y = self.y
        w = self.w
        if self.selected and not suppress_selected:
            color_dark = _COLOR_SELECTED_DARK
            color_light = _COLOR_SELECTED_LIGHT
        else:
            color_dark = _COLOR_BLOCK_DARK
            color_light = _COLOR_BLOCK_LIGHT
        _display = ml.ui.display
        _rect = _display.rect
        _text = _display.text_box
        if only_value:
            yy = y + _LABEL_H
            _rect(x, yy, w, _VALUE_H, color_dark, True) # type: ignore (temporary)
        else:
            _rect(x, y, w, _LABEL_H, color_light, True) # type: ignore (temporary)
            _text(x, y, w, _LABEL_H, self.label, color_light, color_dark, _ALIGN_CENTRE)
            yy = y + _LABEL_H
            _rect(x, yy, w, _VALUE_H, color_dark, True) # type: ignore (temporary)
        yy += 1
        if self.enabled:
            text = _ICON_CHECKED if self.checked else _ICON_UNCHECKED
            _text(x, yy, w, _VALUE_H - 2, text, color_dark, color_light, _ALIGN_CENTRE)
        if self.add_line:
            _rect(x, y + _BLOCK_H - 2, w, 2, _COLOR_LINE, True) # type: ignore (temporary)

    def set_label(self, label: str, redraw: bool = True):
        '''set text for label part of block; called by Pages*._set_*_options'''
        self.label = label
        if redraw:
            self.draw()

    def set_checked(self, checked: bool, redraw: bool = True) -> None:
        '''set checked status; called by Pages*._set_*_options'''
        self.checked = checked
        if redraw:
            self.draw()

    def encoder(self, value: int) -> bool:
        '''process value encoder input at block level, switching check status (ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page >
        Block: *.encoder); called by Pages.encoder'''
        if not self.selected:
            return False
        self.checked = (checked := not self.checked)
        if (_callback_func := self._callback_func) is not None:
            _callback_func(self.id, int(checked))
        return True

    def button_sel_opt(self) -> bool:
        '''process select button press at block level, swithing check status; called by Page.button_sel_opt'''
        if not self.selected:
            return False
        self.checked = (checked := not self.checked)
        if (_callback_func := self._callback_func) is not None:
            _callback_func(self.id, int(checked))
        return True

    def button_del(self) -> bool:
        '''process backspace button press at block level, setting check status to unchecked; called by Page.button_del'''
        if not self.selected:
            return False
        self.checked = self.default_selection
        if (_callback_func := self._callback_func) is not None:
            _callback_func(self.id, 0)
        return True

class SelectBlock(Block):
    '''class providing value select block for ui pages; initiated by Page*._build_sub_page'''

    def __init__(self, id, row: int, col: int, cols: int, cols_per_row: int, selected: bool, label: str = '', options = (),
                 selection: int = 0, default_selection: int = _NONE, add_line: bool = False, callback_func=None) -> None:
        super().__init__(id, row, col, cols, cols_per_row, selected, label, add_line)
        self.options = options
        self.selection = selection
        self.new_selection = selection
        self.default_selection = default_selection
        self._callback_func = callback_func

    def update(self, selected: bool, redraw: bool = True, encoder_id: int = _ENCODER_VAL) -> None:
        '''update block, set selection state and redraw if necessary; called by PopUp.open, PopUp.close, ui.process_user_input,
        Page.set_visibility, Page.set_page_encoders, Page.encoder and Page*.program_change and Page._draw'''
        self.selected = selected
        selection = self.selection
        if selected:
            encoder = ml.ui.encoder_nav if encoder_id == _ENCODER_NAV else ml.ui.encoder_val
            encoder.set(selection, len(self.options) - 1)
        elif selection != self.new_selection:
            self.new_selection = selection
        if redraw:
            self.draw()

    def draw(self, suppress_selected: bool = False, only_value: bool = False) -> None:
        '''draw whole block or only value part of block; called by self.update, self.set_label, self.set_options, self.set_selection
        and Page._draw'''
        if self.totally_hidden:
            return
        if not self.visible:
            ml.ui.display.rect(self.x, self.y, self.w, _BLOCK_H, _COLOR_BLOCK_DARK, True) # type: ignore (temporary)
            return
        x = self.x
        y = self.y
        w = self.w
        if self.selected and not suppress_selected:
            color_dark = _COLOR_SELECTED_CHANGED if self.selection != self.new_selection else _COLOR_SELECTED_DARK
            color_light = _COLOR_SELECTED_LIGHT
        else:
            color_dark = _COLOR_BLOCK_DARK
            color_light = _COLOR_BLOCK_LIGHT
        _display = ml.ui.display
        _rect = _display.rect
        _text = _display.text_box
        if only_value:
            yy = y + _LABEL_H
            _rect(x, yy, w, _VALUE_H, color_dark, True) # type: ignore (temporary)
            yy += 1
        else:
            _rect(x, y, w, _LABEL_H, color_light, True) # type: ignore (temporary)
            _text(x, y, w, _LABEL_H, self.label, color_light, color_dark, _ALIGN_CENTRE)
            yy = y + _LABEL_H
            _rect(x, yy, w, _VALUE_H, color_dark, True) # type: ignore (temporary)
            yy += 1
        if self.new_selection < len(self.options):
            value = self.options[self.new_selection]
        else:
            value = ''
        _text(x, yy, w, _VALUE_H - 2, value, color_dark, color_light, _ALIGN_CENTRE)
        if self.add_line:
            _rect(x, y + _BLOCK_H - 2, w, 2, _COLOR_LINE, True) # type: ignore (temporary)

    def set_label(self, label: str, redraw: bool = True):
        '''set text for label part of block; called by Pages*._set_*_options'''
        self.label = label
        if redraw:
            self.draw()

    def set_options(self, options = None, selection: int = 0, default_selection: int = _NONE, redraw: bool = True) -> None:
        '''set list of options and current selection; called by self.set_selection and Pages*._set_*_options'''
        if options is None:
            options = self.options
        else:
            if len(options) == 0:
                options = EMPTY_OPTIONS_BLANK
            self.options = options
            _ui = ml.ui
            if self.selected and not _ui.page_select_mode:
                _ui.encoder_val.set(selection, len(options) - 1)
        self.selection = selection
        self.new_selection = selection
        if default_selection != _NONE:
            self.default_selection = default_selection
        if redraw:
            self.draw()

    def set_selection(self, selection: int) -> bool:
        '''set list of options and current selecstion; called by self.encoder, self.button_del and Page*.midi_learn'''
        if self.new_selection == selection:
            return False
        self.new_selection = selection
        self.draw(only_value=True)
        return True

    def encoder(self, value: int) -> bool:
        '''process value encoder input at block level (ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by Pages.encoder'''
        if not self.selected:
            return False
        return self.set_selection(value)

    def button_sel_opt(self) -> bool:
        '''process select button press at block level storing changed selection if applicable, otherwise calling context menu/function;
        called by Page.button_sel_opt'''
        if not self.selected:
            return False
        if (_callback_func := self._callback_func) is not None:
            if self.selection == (new_selection := self.new_selection):
                _callback_func(self.id, button_sel_opt=True)
            else:
                self.selection = new_selection
                _callback_func(self.id, new_selection)
        return True

    def button_del(self) -> bool:
        '''process backspace button press at block level; called by Page.button_del'''
        if not self.selected:
            return False
        if (default_selection := self.default_selection) == _NONE:
            if (_callback_func := self._callback_func) is not None:
                _callback_func(self.id, button_del=True)
        else:
            self.set_selection(default_selection)
        return True

class TextBlock(Block):
    '''class providing text block to be used with editing option or button actions, for ui pages; initiated by Page*._build_sub_page'''

    def __init__(self, id, row: int, col: int, cols: int, cols_per_row: int, selected: bool, label: str = '', value: str = '',
                 add_line: bool = False, callback_func=None) -> None:
        super().__init__(id, row, col, cols, cols_per_row, selected, label, add_line)
        self.value = value
        self._callback_func = callback_func

    def update(self, selected: bool, redraw: bool = True, encoder_id: int = _ENCODER_VAL) -> None:
        '''update block, set selection state and redraw if necessary; called by PopUp.open, PopUp.close, ui.process_user_input,
        Page.set_visibility, Page.set_page_encoders, Page.encoder and Page*.program_change and Page._draw'''
        self.selected = selected
        if redraw:
            self.draw()

    def draw(self, suppress_selected: bool = False, only_value: bool = False) -> None:
        '''draw whole block or only value part of block; called by self.update, self.set_label, self.set_options, self.set_selection
        and Page._draw'''
        if self.totally_hidden:
            return
        if not self.visible:
            ml.ui.display.rect(self.x, self.y, self.w, _BLOCK_H, _COLOR_BLOCK_DARK, True) # type: ignore (temporary)
            return
        x = self.x
        y = self.y
        w = self.w
        if self.selected and not suppress_selected:
            color_dark = _COLOR_SELECTED_DARK
            color_light = _COLOR_SELECTED_LIGHT
        else:
            color_dark = _COLOR_BLOCK_DARK
            color_light = _COLOR_BLOCK_LIGHT
        _display = ml.ui.display
        _rect = _display.rect
        _text = _display.text_box
        if only_value:
            yy = y + _LABEL_H
            _rect(x, yy, w, _VALUE_H, color_dark, True) # type: ignore (temporary)
        else:
            _rect(x, y, w, _LABEL_H, color_light, True) # type: ignore (temporary)
            _text(x, y, w, _LABEL_H, self.label, color_light, color_dark, _ALIGN_CENTRE)
            yy = y + _LABEL_H
            _rect(x, yy, w, _VALUE_H, color_dark, True) # type: ignore (temporary)
        yy += 1
        _text(x, yy, w, _VALUE_H - 2, self.value, color_dark, color_light, _ALIGN_CENTRE)
        if self.add_line:
            _rect(x, y + _BLOCK_H - 2, w, 2, _COLOR_LINE, True) # type: ignore (temporary)

    def set_label(self, label: str, redraw: bool = True):
        '''set text for label part of block; called by Pages*._set_*_options'''
        self.label = label
        if redraw:
            self.draw()

    def set_value(self, value: str, redraw: bool = True) -> None:
        '''set value; called Pages*._set_*_options'''
        self.value = value
        if redraw:
            self.draw()

    def button_sel_opt(self) -> bool:
        '''process select button press at block level calling context menu/function; called by Page.button_'''
        if not self.selected:
            return False
        if (_callback_func := self._callback_func) is not None:
            _callback_func(self.id, button_sel_opt=True)
        return True

    def button_del(self) -> bool:
        '''process backspace button press at block level; called by Page.button_del'''
        if not self.selected:
            return False
        if (_callback_func := self._callback_func) is not None:
            _callback_func(self.id, button_del=True)
        return True

class TextRow():
    '''class providing text row block for monitor page and to for text row at bottom of matrix page; initiated by _Monitor.draw and
    PageMatrix._build_page'''

    def __init__(self, y: int, h: int, back_color: int, fore_color: int, align: int = _ALIGN_LEFT) -> None:
        self.y = y
        self.h = h
        self.back_color = back_color
        self.fore_color = fore_color
        self.align = align

    def set_text(self, text: str, redraw: bool = False) -> None:
        '''set text row text; called by _Monitor.draw and Page*._set_text_row'''
        self.text = text
        if not redraw:
            return
        _display = ml.ui.display
        _display.rect(0, (y := self.y), _SUB_PAGE_W, (h := self.h), (back_color := self.back_color), True) # type: ignore (temporary)
        _display.text_box(1, y, _SUB_PAGE_W - 2, h, text, back_color, self.fore_color, self.align)

    def draw(self) -> None:
        '''draw text row; called by Page._draw'''
        _display = ml.ui.display
        _display.rect(0, (y := self.y), _SUB_PAGE_W, (h := self.h), (back_color := self.back_color), True) # type: ignore (temporary)
        _display.text_box(1, y, _SUB_PAGE_W - 2, h, self.text, back_color, self.fore_color, self.align)

class PopUp():
    '''base class for pop-ups'''

    def __init__(self, id: int) -> None:
        self.id = id
        self.inside_w = 0
        self.inside_h = 0
        self.visible = False

    def open(self, frame) -> None:
        '''open and draw pop-up and deselect selected page block; called by PopUp*.open'''
        self.frame = frame
        self.visible = True
        _ui = ml.ui
        _ui.active_pop_up = self # type: ignore
        active_page = _ui.frames[_ui.active_frame]
        if len(active_page.blocks) > 0:
            active_page.blocks[active_page.selected_block[active_page.sub_page]].update(False)
        self.w = self.inside_w + 2 * _MARGIN_LARGE
        self.h = self.inside_h + 2 * _MARGIN_LARGE
        self.x = self.frame.x + (self.frame.w - self.w) // 2
        self.y = self.frame.y + (self.frame.h - self.h) // 2
        self.draw()

    def draw(self) -> None:
        '''draw pop-up; called by PopUp.open, *PopUp.encoder and Page._draw'''
        pass

    def close(self) -> None:
        '''close pop-up and resselect selected page block; called by self.button_no, self.button_yes, *PopUp.button_sel_opt,
        and ui.process_user_input'''
        _ui = ml.ui
        _ui.active_pop_up = None
        self.visible = False
        active_page = _ui.frames[_ui.active_frame]
        if len(active_page.blocks) > 0:
            active_page.blocks[active_page.selected_block[active_page.sub_page]].update(True, False)

    def encoder(self, encoder_id: int, value: int) -> bool:
        '''process encoder input at pop-up level (ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by ui.process_encoder_input'''
        return False

    def button_sel_opt(self) -> bool:
        '''process select button press at pop-up level; called by *PopUp.button_yes and ui.process_user_input'''
        return False

    def button_del(self) -> bool:
        '''process backspace button press at pop-up level; called by Page.process_user_input'''
        return False

    def button_no(self) -> bool:
        '''process cancel button at pop-up level; called by ui.process_user_input'''
        self.close()
        return True

    def button_yes(self) -> bool:
        '''process confirm button at pop-up level; called by ui.process_user_input'''
        self.close()
        return True

    def _draw_background(self):
        '''draw pop-up background; called by self.draw'''
        _rect = ml.ui.display.rect
        x = self.x
        y = self.y
        w = self.w
        h = self.h
        for i in range(_MARGIN):
            _rect(x + i, y + i, w - 2 * i, h - 2 * i, _COLOR_BLOCK_DARK)
        _rect(x + _MARGIN, y + _MARGIN, w - 2 * _MARGIN, h - 2 * _MARGIN, _COLOR_POP_UP_DARK, True) # type: ignore (temporary)
        
class TextEdit(PopUp):
    '''class providing text edit pop-up; initiated once by ui.__init__'''

    def __init__(self, id: int) -> None:
        super().__init__(id)
        self.inside_w = _CHARACTER_COLUMNS * _CHAR_W + 1
        self.x = 0
        self.y = 0
        self.input_w = self.inside_w - 2 * _MARGIN
        self.cursor_y = (_TEXT_H - _CURSOR_H) // 2

    def open(self, frame, caller_id: int, text: str, max_characters: int = 27, is_file_name: bool = False, callback_func=None) -> None:
        '''open and draw pop-up and deselect selected page block; called by ui._save_program_confirm, Page*.process_user_input
        and PageProgram._callback_menu'''
        self.caller_id = caller_id
        self.text = text
        self.max_characters = max_characters
        self.is_file_name = is_file_name
        self._callback_func = callback_func
        characters = _INPUT_CHARS_FILE if is_file_name else _INPUT_CHARS
        self.characters = characters
        self.character_rows = -(-len(characters) // _CHARACTER_COLUMNS)
        self.inside_h = _TEXT_H + _MARGIN + (self.character_rows + 1) * _CHAR_H + 1
        _ui = ml.ui
        self.cursor_w, _ = _ui.display.get_text_bounds('0')
        self.store_x = 0
        self.selection_x = _NONE
        self.selection_y = _NONE
        super().open(frame)
        self._update_selection(0, 0)
        _ui.encoder_nav.set(0, self.character_rows)
        _ui.encoder_val.set(0, _CHARACTER_COLUMNS - 1)

    def draw(self) -> None:
        '''draw pop-up; called by self.open and Page._draw'''
        _display = ml.ui.display
        _text = _display.text_box
        self._draw_background()
        _display.rect((xx := self.x + _MARGIN_LARGE), (yy := self.y + _MARGIN_LARGE), self.inside_w, _TEXT_H,
                      _COLOR_POP_UP_LIGHT, True) # type: ignore (temporary)
        yy += _TEXT_H + _MARGIN
        for i, ch in enumerate(self.characters):
            _text(xx + (i % _CHARACTER_COLUMNS) * _CHAR_W, yy + (i // _CHARACTER_COLUMNS) * _CHAR_H, _CHAR_W, _CHAR_H, ch,
                  _COLOR_POP_UP_DARK, _COLOR_POP_UP_LIGHT, _ALIGN_CENTRE)
        _text(xx, yy + self.character_rows * _CHAR_H, self.input_w, _CHAR_W,
              _TEXT_INPUT_SPACE_BAR, _COLOR_POP_UP_DARK, _COLOR_POP_UP_LIGHT, _ALIGN_CENTRE)
        self._draw_input_text()

    def encoder(self, encoder_id: int, value: int) -> bool:
        '''process encoder input at pop-up level (ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by ui.process_encoder_input'''
        if encoder_id == _ENCODER_NAV:
            return self._update_selection(y=value)
        return self._update_selection(x=value)

    def button_sel_opt(self) -> bool:
        '''process select button press at pop-up level; called by ui.process_user_input'''
        if len(self.text) >= _TEXT_INPUT_MAX_LENGTH:
            return False
        if self.selection_y < self.character_rows:
            pos = self.selection_y * _CHARACTER_COLUMNS + self.selection_x
            self.text += self.characters[pos]
        else:
            self.text += ' '
        self._draw_input_text()
        return True

    def button_del(self) -> bool:
        '''process backspace button press at pop-up level; called by Page.process_user_input'''
        if len(self.text) > 0:
            self.text = self.text[:-1]
            self._draw_input_text()
            return True
        return False

    def button_yes(self) -> bool:
        '''process confirm button at pop-up level; called by ui.process_user_input'''
        self.close()
        if (_callback_func := self._callback_func) is not None:
            _callback_func(self.caller_id, self.text.strip())
        return True

    def _draw_input_text(self) -> None:
        '''draw or update text being edited; called by self.draw, self.button_sel_opt and self.button_del'''
        text = self.text
        x = self.x + _MARGIN_LARGE + _MARGIN
        y = self.y + _MARGIN_LARGE
        _display = ml.ui.display
        _rect = _display.rect
        _rect(x, y, (input_w := self.input_w), _TEXT_H, _COLOR_POP_UP_LIGHT, True) # type: ignore (temporary)
        _display.text_box(x, y, input_w, _TEXT_H, text, _COLOR_POP_UP_LIGHT, _COLOR_POP_UP_DARK, _ALIGN_LEFT)
        x0, y0, tw, th = _display.get_text_box_bounds(x, y, input_w, _TEXT_H, text, _ALIGN_LEFT)
        cursor_w = self.cursor_w
        if len(text) >= _TEXT_INPUT_MAX_LENGTH:
            cursor_x = x + input_w - cursor_w
        else:
            cursor_x = x0 + tw + 1
        _rect(cursor_x, y0 + th - 1, cursor_w, 2, _COLOR_POP_UP_DARK, True) # type: ignore (temporary)

    def _update_selection(self, x: int|None = None, y: int|None = None) -> bool:
        '''update input character (or space bar) selection; called by self.open and self.encoder'''
        previous_x = self.selection_x
        previous_y = self.selection_y
        if x is None:
            x = self.store_x
        else:
            self.store_x = x
        if y is None:
            y = previous_y
            row_changed = False
        else:
            if (row_changed := self.selection_y != y):
                self.selection_y = y
        if previous_x == x and previous_y == y:
            return False
        n = len(self.characters)
        if y != self.character_rows and y == n // _CHARACTER_COLUMNS and y * _CHARACTER_COLUMNS + x >= n:
            if row_changed:
                x = n - y * _CHARACTER_COLUMNS - 1
            else:
                x = n - y * _CHARACTER_COLUMNS - 1 if x == _CHARACTER_COLUMNS - 1 else 0                    
                self.store_x = x
                ml.ui.encoder_val.set(x)
        self.selection_x = x
        if previous_x is not None and previous_y is not None:
            self._draw_selection(previous_x, previous_y, False)
        self._draw_selection(x, y, True)
        return True

    def _draw_selection(self, selection_x: int, selection_y: int, selected: bool) -> None:
        '''draw input character (or space bar) to be selected on deselected; called by self._update_selection'''
        if selected:
            fore_color = _COLOR_POP_UP_DARK
            back_color = _COLOR_POP_UP_LIGHT
        else:
            fore_color = _COLOR_POP_UP_LIGHT
            back_color = _COLOR_POP_UP_DARK
        if selection_y < self.character_rows:
            text = self.characters[selection_y * _CHARACTER_COLUMNS + selection_x]
            x = self.x + _MARGIN_LARGE + selection_x * _CHAR_W
            w = _CHAR_W
        else:
            text = _TEXT_INPUT_SPACE_BAR
            x = self.x + _MARGIN_LARGE
            w = self.input_w
        _display = ml.ui.display
        y =self.y + _MARGIN_LARGE + _TEXT_H + _MARGIN + selection_y * _CHAR_H
        _display.rect(x, y, w, _CHAR_H, back_color, True) # type: ignore (temporary)
        _display.text_box(x, y, w, _CHAR_H, text, back_color, fore_color, _ALIGN_CENTRE)

class SelectPopUp(PopUp):
    '''class providing value select pop-up; initiated once by ui.__init__'''

    def __init__(self, id: int) -> None:
        super().__init__(id)
        self.inside_w = _SELECT_TRIGGER_W
        self.inside_h = _POP_UP_LABEL_H + _VALUE_H

    def open(self, frame, caller_id: int, label: str, options: list|tuple, selection: int, callback_func=None) -> None:
        '''open and draw pop-up and deselect selected page block; called by Page*.process_user_input and PageMatrix.button_sel_opt'''
        self.caller_id = caller_id
        self.label = label
        self.options = options
        self.selection = selection
        self._callback_func = callback_func
        super().open(frame)

    def draw(self, only_value: bool=False) -> None:
        '''draw pop-up; called by self.open and self.encoder'''
        _ui = ml.ui
        _ui.encoder_val.set(self.selection, len(self.options) - 1)
        value = '' if len(self.options) == 0 else self.options[self.selection]
        inside_w = self.inside_w
        _display = _ui.display
        _rect = _display.rect
        _text = _display.text_box
        if only_value:
            x = self.x + _MARGIN_LARGE
            y = self.y + _MARGIN_LARGE + _POP_UP_LABEL_H
            _rect(x,y, inside_w, _VALUE_H, _COLOR_POP_UP_LIGHT, True) # type: ignore (temporary)
            _text(x, y, inside_w, _VALUE_H, value, _COLOR_POP_UP_LIGHT, _COLOR_POP_UP_DARK, _ALIGN_CENTRE)
            return
        self._draw_background()
        x = self.x + _MARGIN_LARGE
        y = self.y + _MARGIN_LARGE
        _text(x, y, inside_w, _POP_UP_LABEL_H, self.label, _COLOR_POP_UP_DARK, _COLOR_POP_UP_LIGHT, _ALIGN_CENTRE)
        y += _POP_UP_LABEL_H
        _rect(x, y, inside_w, _VALUE_H, _COLOR_POP_UP_LIGHT, True) # type: ignore (temporary)
        _text(x, y, inside_w, _VALUE_H, value, _COLOR_POP_UP_LIGHT, _COLOR_POP_UP_DARK, _ALIGN_CENTRE)

    def encoder(self, encoder_id: int, value: int) -> bool:
        '''process value encoder input at pop-up level (ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by ui.process_encoder_input'''
        if encoder_id != _ENCODER_VAL:
            return False
        self.selection = value
        self.draw(True)
        return True

    def button_sel_opt(self) -> bool:
        '''process select button press at pop-up level; called by self.button_yes and ui.process_user_input'''
        self.close()
        if (_callback_func := self._callback_func) is not None:
            _callback_func(self.caller_id, self.selection)
        return True

    def button_yes(self) -> bool:
        '''process confirm button at pop-up level; called by ui.process_user_input'''
        self.button_sel_opt()
        return True

class MenuPopUp(PopUp):
    '''class providing menu pop-up; initiated once by ui.__init__'''

    def __init__(self, id: int) -> None:
        super().__init__(id)
        self.inside_w = _MENU_W
        self.selection = 0

    def open(self, frame, options: tuple, selection: int = 0, callback_func=None) -> None:
        '''open and draw pop-up and deselect selected page block; called by Page*.process_user_input'''
        self.options = options
        self.selection = selection
        self._callback_func = callback_func
        self.inside_h = len(options) * _CONTROL_H
        super().open(frame)

    def draw(self) -> None:
        '''draw pop-up; called by self.open and self.encoder'''
        _ui = ml.ui
        _display = _ui.display
        _rect = _display.rect
        _text = _display.text_box
        inside_w = self.inside_w
        text_w = inside_w - 2 * _MARGIN
        self._draw_background()
        x = self.x + _MARGIN_LARGE
        y = self.y + _MARGIN_LARGE
        _ui.encoder_val.set((selection := self.selection), len(options := self.options) - 1)
        for i, option in enumerate(options):
            if i == selection:
                _rect(x, y, inside_w, _CONTROL_H, _COLOR_POP_UP_LIGHT, True) # type: ignore (temporary)
                back_color = _COLOR_POP_UP_LIGHT
                fore_color = _COLOR_POP_UP_DARK
            else:
                back_color = _COLOR_POP_UP_DARK
                fore_color = _COLOR_POP_UP_LIGHT
            _text(x + _MARGIN, y, text_w, _CONTROL_H, option, back_color, fore_color, _ALIGN_CENTRE)
            y += _CONTROL_H

    def encoder(self, encoder_id: int, value: int) -> bool:
        '''process value encoder input at pop-up level (ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by ui.process_encoder_input'''
        if encoder_id != _ENCODER_VAL:
            return False
        self.selection = value
        self.draw()
        return True

    def button_sel_opt(self) -> bool:
        '''process select button press at pop-up level; called by self.button_yes and ui.process_user_input'''
        self.close()
        if (_callback_func := self._callback_func) is not None:
            _callback_func(self.selection)
        return True

    def button_yes(self) -> bool:
        '''process confirm button at pop-up level; called by ui.process_user_input'''
        self.button_sel_opt()
        return True

class ConfirmPopUp(PopUp):
    '''class providing confirmation pop-up; initiated once by ui.__init__'''

    def __init__(self, id: int) -> None:
        super().__init__(id)
        self.inside_w = _CONFIRM_W
        self.inside_h = _CONTROL_H
        self.selection = 0

    def open(self, frame, caller_id: int, label, callback_func=None) -> None:
        '''open and draw pop-up and deselect selected page block; called by ui.save_program, ui.save_program_confirm,
        Page*.process_user_input and PageMatrix._callback_select'''
        self.caller_id = caller_id
        self.label = label
        self._callback_func = callback_func
        super().open(frame)

    def draw(self) -> None:
        '''draw pop-up; called by self.open and self.encoder'''
        self._draw_background()
        ml.ui.display.text_box(self.x + _MARGIN_LARGE, self.y + _MARGIN_LARGE, self.inside_w, _CONTROL_H, self.label,
                               _COLOR_POP_UP_DARK, _COLOR_POP_UP_LIGHT, _ALIGN_CENTRE)

    def button_no(self) -> bool:
        '''process cancel button at pop-up level; called by ui.process_user_input'''
        self.close()
        if (_callback_func := self._callback_func) is not None:
            _callback_func(self.caller_id, False)
        return True

    def button_yes(self) -> bool:
        '''process confirm button at pop-up level; called by ui.process_user_input'''
        self.close()
        if (_callback_func := self._callback_func) is not None:
            _callback_func(self.caller_id, True)
        return True

class MessagePopUp(PopUp):
    '''class providing message pop-up; initiated once by ui.__init__'''

    def __init__(self, id: int) -> None:
        super().__init__(id)
        self.inside_w = _CONFIRM_W
        self.inside_h = _CONTROL_H
        self.selection = 0

    def open(self, frame, label, allow_close: bool = True) -> None:
        '''open and draw pop-up and deselect selected page block; called by PageMatrix._callback_select'''
        self.label = label
        self.allow_close = allow_close
        super().open(frame)

    def draw(self) -> None:
        '''draw pop-up; called by self.open and self.encoder'''
        self._draw_background()
        ml.ui.display.text_box(self.x + _MARGIN_LARGE, self.y + _MARGIN_LARGE, self.inside_w, _CONTROL_H, self.label,
                               _COLOR_POP_UP_DARK, _COLOR_POP_UP_LIGHT, _ALIGN_CENTRE)

    def button_no(self) -> bool:
        '''process cancel button at pop-up level; called by ui.process_user_input'''
        if self.allow_close:
            self.close()
            return True
        return False

    def button_yes(self) -> bool:
        '''process confirm button at pop-up level; called by ui.process_user_input'''
        if self.allow_close:
            self.close()
            return True
        return False

    def button_sel_opt(self) -> bool:
        '''process select button press at pop-up level; called by *PopUp.button_yes and ui.process_user_input'''
        if self.allow_close:
            self.close()
            return True
        return False

    def button_del(self) -> bool:
        '''process backspace button press at pop-up level; called by Page.process_user_input'''
        if self.allow_close:
            self.close()
            return True
        return False

class ProgramPopUp(PopUp):
    '''class providing chord select pop-up; initiated once by ui.__init__'''

    def __init__(self, id: int) -> None:
        super().__init__(id)
        self.inside_w = _SELECT_TRIGGER_W
        self.inside_h = 2 * (_POP_UP_LABEL_H + _VALUE_H)

    def open(self, frame, labels: tuple[str, str], bank: int, program: int, callback_func=None) -> None:
        '''open and draw pop-up and deselect selected page block; called by ui.process_user_input, ui.save_program,
        ui._callback_confirm and PageProgram._callback_menu'''
        self.labels = labels
        self.bank = bank
        self.program = program
        self._callback_func = callback_func
        self.active_input = 1
        ml.ui.encoder_nav.set(1, 1)
        super().open(frame)

    def draw(self, only_value: bool=False) -> None:
        '''draw pop-up; called by self.open and self.encoder'''
        _ml = ml
        _ui = _ml.ui
        _data = _ml.data
        active_input = self.active_input
        _display = _ui.display
        _rect = _display.rect
        _text = _display.text_box
        bank = self.bank
        program = self.program
        if only_value:
            x = self.x + _MARGIN_LARGE
            y = self.y + _MARGIN_LARGE + _POP_UP_LABEL_H
            inside_w = self.inside_w
            if active_input == 0: # bank
                value = chr(_ASCII_A + bank)
                _rect(x, y, inside_w, _VALUE_H, _COLOR_POP_UP_LIGHT, True) # type: ignore (temporary)
                _text(x, y, inside_w, _VALUE_H, value, _COLOR_POP_UP_LIGHT, _COLOR_POP_UP_DARK, _ALIGN_CENTRE)
            y += _POP_UP_LABEL_H + _VALUE_H
            fore_color = _COLOR_POP_UP_INACTIVE if active_input == 0 else _COLOR_POP_UP_LIGHT
            value = _data.get_program_name(bank, program)
            _rect(x, y, inside_w, _VALUE_H, fore_color, True) # type: ignore (temporary)
            _text(x, y, inside_w, _VALUE_H, value, fore_color, _COLOR_POP_UP_DARK, _ALIGN_CENTRE)
            return
        if active_input == 0: # bank
            _ui.encoder_val.set(bank, 25)
        else: # program
            _ui.encoder_val.set(program, 99)
        self._draw_background()
        x = self.x + _MARGIN_LARGE
        y = self.y + _MARGIN_LARGE
        labels = self.labels
        for i in range(2):
            fore_color = _COLOR_POP_UP_LIGHT if active_input == i else _COLOR_POP_UP_INACTIVE
            if i == 0:
                label = labels[0]
                value = chr(_ASCII_A + bank)
            else:
                label = labels[1]
                value = _data.get_program_name(bank, program)
            _text(x, y, (inside_w := self.inside_w), _POP_UP_LABEL_H, label, _COLOR_POP_UP_DARK, fore_color, _ALIGN_CENTRE)
            y += _POP_UP_LABEL_H
            _rect(x, y, inside_w, _VALUE_H, fore_color, True) # type: ignore (temporary)
            _text(x, y, inside_w, _VALUE_H, value, fore_color, _COLOR_POP_UP_DARK, _ALIGN_CENTRE)
            y += _VALUE_H

    def encoder(self, encoder_id: int, value: int) -> bool:
        '''process value encoder input at pop-up level (ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by ui.process_encoder_input'''
        if encoder_id == _ENCODER_NAV:
            self.active_input = value
            only_value = False
        else: # encoder_id == _ENCODER_VAL
            active_input = self.active_input
            if active_input == 0: # bank
                self.bank = value
                self.program = 0
            else: # program
                self.program = value
            only_value = True
        self.draw(only_value)
        return True

    def button_sel_opt(self) -> bool:
        '''process select button press at pop-up level; called by self.button_yes and ui.process_user_input'''
        self.close()
        if (_callback_func := self._callback_func) is not None:
            _callback_func(self.bank, self.program)
        return True

    def button_yes(self) -> bool:
        '''process confirm button at pop-up level; called by ui.process_user_input'''
        self.button_sel_opt()
        return True

class TriggerPopUp(PopUp):
    '''class providing trigger selection pop-up; initiated once by ui.__init__'''

    def __init__(self, id: int) -> None:
        super().__init__(id)
        self.inside_w = _TRIGGER_W * _MATRIX_COLUMNS
        self.inside_h = _TRIGGER_H * _MATRIX_ROWS + 2 * _MARGIN + _TEXT_ROW_H
        self.x = 0
        self.y = 0
        self.triggers = []
        self.selection = None

    def open(self, frame, caller_id: int, callback_func=None) -> None:
        '''open and draw pop-up and deselect selected page block; called by ui.process_user_input and PageProgram.process_user_input'''
        self.caller_id = caller_id
        self._callback_func = callback_func
        triggers = self.triggers
        triggers.clear()
        _router = ml.router
        trigger_matrix = _router.trigger_matrix
        trigger_zones = _router.trigger_zones
        input_trigger = _router.input_trigger
        n = 0
        selection = 0
        for i in range(_MATRIX_ROWS):
            for j in range(_MATRIX_COLUMNS):
                trigger = trigger_matrix[i][j]
                if trigger != _NONE:
                    zone = trigger_zones[i][j]
                    triggers.append([i, j, trigger, zone]) # _TRIGGER_ROW, _TRIGGER_COL, _TRIGGER_TRIGGER, _TRIGGER_ZONE
                    if trigger == input_trigger:
                        selection = n
                    n += 1
        self.selection = selection
        super().open(frame)
        self._update_selection()
        ml.ui.encoder_nav.set(selection, len(triggers) - 1)

    def draw(self) -> None:
        '''draw pop-up; called by self.open and Page._draw'''
        trigger_defs = TRIGGERS
        triggers_short = TRIGGERS_SHORT
        _display = ml.ui.display
        _line = _display.line
        _rect = _display.rect
        _text = _display.text_box
        self._draw_background()
        selection = self.selection
        y1 = (y := self.y + _MARGIN_LARGE) + _TRIGGER_H // 2
        x2 = (x := self.x + _MARGIN_LARGE) + self.inside_w - 1
        for i in range(_MATRIX_ROWS):
            _line(x, (yy := y1 + i * _TRIGGER_H), x2, yy, _COLOR_POP_UP_INACTIVE)
        x1 = x + _TRIGGER_W // 2
        y2 = y + _MATRIX_ROWS * _TRIGGER_H - 1
        for i in range(_MATRIX_COLUMNS):
            _line((xx := x1 + i * _TRIGGER_W), y, xx, y2, _COLOR_POP_UP_INACTIVE)
        for i, (row, col, trigger, zone) in enumerate(self.triggers):
            if selection == i:
                continue
            _rect((xx := x + col * _TRIGGER_W), (yy := y + row * _TRIGGER_H), _TRIGGER_W, _TRIGGER_H, _COLOR_POP_UP_DARK, True) # type: ignore (temporary)
            _text(xx, yy, _TRIGGER_W, _TRIGGER_H, f'{triggers_short[trigger]}{trigger_defs[trigger][2][0][zone]}',
                  _COLOR_POP_UP_DARK, _COLOR_POP_UP_LIGHT, _ALIGN_CENTRE)

    def encoder(self, encoder_id: int, value: int) -> bool:
        '''process encoder input at pop-up level (ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by ui.process_encoder_input'''
        if encoder_id == _ENCODER_NAV:
            return self._update_selection(value)
        self._update(zone=value)
        return True

    def button_sel_opt(self) -> bool:
        '''process select button press at pop-up level; called by ui.process_user_input'''
        self.close()
        trigger_arr = self.triggers[self.selection] # type: ignore
        if (_callback_func := self._callback_func) is not None:
            _callback_func(trigger_arr[_TRIGGER_TRIGGER], trigger_arr[_TRIGGER_ZONE])
        return True

    def button_yes(self) -> bool:
        '''process confirm button at pop-up level; called by ui.process_user_input'''
        self.close()
        trigger_arr = self.triggers[self.selection] # type: ignore
        if (_callback_func := self._callback_func) is not None:
            _callback_func(trigger_arr[_TRIGGER_TRIGGER], trigger_arr[_TRIGGER_ZONE])
        return True

    def _update_selection(self, selection: int|None = None) -> bool:
        '''update trigger selection (cursor); called by self.open and self.encoder'''
        old_selection = self.selection
        if selection is None:
            selection = old_selection
        elif old_selection == selection:
            return False
        if old_selection is not None and old_selection != selection:
            self._update(old_selection, selected=False)
        self.selection = selection
        self._update(selection)
        return True

    def _update(self, selection: int|None = None, zone: int|None = None, selected: bool = True) -> None:
        '''draw trigger string to be updated; called by self.encoder and self._update_selection'''
        sel = self.selection if selection is None else selection
        trigger_arr = self.triggers[sel] # type: ignore
        if zone is None:
            zone = trigger_arr[_TRIGGER_ZONE]
        else:
            trigger_arr[_TRIGGER_ZONE] = zone
        _ui = ml.ui
        trigger_defs = TRIGGERS
        trigger = trigger_arr[_TRIGGER_TRIGGER]
        if selected:
            zones = trigger_defs[trigger][2][1]
            if selection is not None:
                _ui.encoder_val.set(0, len(zones) - 1)
            back_color = _COLOR_POP_UP_LIGHT
            fore_color = _COLOR_POP_UP_DARK
        else:
            back_color = _COLOR_POP_UP_DARK
            fore_color = _COLOR_POP_UP_LIGHT
        xx = (x := self.x + _MARGIN_LARGE) + trigger_arr[_TRIGGER_COL] * _TRIGGER_W
        yy = (y := self.y + _MARGIN_LARGE) + trigger_arr[_TRIGGER_ROW] * _TRIGGER_H
        _display = _ui.display
        _rect = _display.rect
        _text = _display.text_box
        _rect(xx, yy, _TRIGGER_W, _TRIGGER_H, back_color, True) # type: ignore (temporary)
        _text(xx, yy, _TRIGGER_W, _TRIGGER_H, f'{TRIGGERS_SHORT[trigger]}{trigger_defs[trigger][2][0][zone]}',
              back_color, fore_color, _ALIGN_CENTRE)
        if selected:
            trigger_long = TRIGGERS_LONG[trigger]
            zone_name = zones[zone]
            text = trigger_long if zone_name == '' else f'{trigger_long}: {zone_name}'
            y += _MATRIX_ROWS * _TRIGGER_H + 2 * _MARGIN
            _rect(x, y, (w := self.inside_w), _TEXT_ROW_H, _COLOR_POP_UP_DARK, True) # type: ignore (temporary)
            _text(x, y, w, _TEXT_ROW_H, text, _COLOR_POP_UP_DARK, _COLOR_POP_UP_INACTIVE, _ALIGN_CENTRE)

class MatrixPopUp(PopUp):
    '''class providing trigger/zone select pop-up; initiated once by ui.__init__'''

    def __init__(self, id: int) -> None:
        super().__init__(id)
        self.inside_w = _SELECT_TRIGGER_W
        self.inside_h = 2 * (_POP_UP_LABEL_H + _VALUE_H)

    def open(self, frame, caller_id: int, trigger: int, zone: int, callback_func=None) -> None:
        '''open and draw pop-up and deselect selected page block; called by ui.process_user_input'''
        self.caller_id = caller_id
        self.trigger = trigger
        self.zone = zone
        self._callback_func = callback_func
        self.active_input = 1
        ml.ui.encoder_nav.set(1, 1)
        super().open(frame)

    def draw(self, only_value: bool=False) -> None:
        '''draw pop-up; called by self.open and self.encoder'''
        _ui = ml.ui
        active_input = self.active_input
        _display = _ui.display
        _rect = _display.rect
        _text = _display.text_box
        triggers_short = TRIGGER_OPTIONS_SHORT
        trigger_name = TRIGGER_OPTIONS_LONG[(trigger := self.trigger) + 1] # _NONE becomes 0
        zone = self.zone
        if trigger == _NONE:
            zone_label = ''
            zone_icons = EMPTY_OPTIONS_BLANK
        else:
            trigger_name = f'{trigger_name} ({triggers_short[trigger + 1]})' # _NONE becomes 0
            zone_labels = TRIGGERS[trigger][2]
            zone_label = zone_labels[1][zone]
            zone_icons = zone_labels[1]
        if zone_label == '':
            zone_name = ''
            self.active_input = (active_input := 0)
            ml.ui.encoder_nav.set(0)
        else:
            zone_name =f'{zone_label} ({zone_icons[zone]})'
        if only_value:
            x = self.x + _MARGIN_LARGE
            y = self.y + _MARGIN_LARGE + active_input * (_POP_UP_LABEL_H + _VALUE_H) + _POP_UP_LABEL_H
            inside_w = self.inside_w
            if active_input == 0: # trigger
                value = trigger_name
                _rect(x, y, inside_w, _VALUE_H, _COLOR_POP_UP_LIGHT, True) # type: ignore (temporary)
                _text(x, y, inside_w, _VALUE_H, value, _COLOR_POP_UP_LIGHT, _COLOR_POP_UP_DARK, _ALIGN_CENTRE)
            y += _POP_UP_LABEL_H + _VALUE_H
            fore_color = _COLOR_POP_UP_INACTIVE if active_input == 0 else _COLOR_POP_UP_LIGHT
            value = zone_name
            _rect(x, y, inside_w, _VALUE_H, fore_color, True) # type: ignore (temporary)
            _text(x, y, inside_w, _VALUE_H, value, fore_color, _COLOR_POP_UP_DARK, _ALIGN_CENTRE)
            return
        if active_input == 0: # trigger
            _ui.encoder_val.set(trigger + 1, len(triggers_short) - 1) # _NONE becomes 0
        else: # zone
            _ui.encoder_val.set(zone, len(zone_icons))
        self._draw_background()
        x = self.x + _MARGIN_LARGE
        y = self.y + _MARGIN_LARGE
        for i in range(2):
            fore_color = _COLOR_POP_UP_LIGHT if active_input == i else _COLOR_POP_UP_INACTIVE
            if i == 0:
                label = 'assign trigger'
                value = trigger_name
            else:
                label = 'set active zone/layer'
                value = zone_name
            _text(x, y, (inside_w := self.inside_w), _POP_UP_LABEL_H, label, _COLOR_POP_UP_DARK, fore_color, _ALIGN_CENTRE)
            y += _POP_UP_LABEL_H
            _rect(x, y, inside_w, _VALUE_H, fore_color, True) # type: ignore (temporary)
            _text(x, y, inside_w, _VALUE_H, value, fore_color, _COLOR_POP_UP_DARK, _ALIGN_CENTRE)
            y += _VALUE_H

    def encoder(self, encoder_id: int, value: int) -> bool:
        '''process value encoder input at pop-up level (ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by ui.process_encoder_input'''
        if encoder_id == _ENCODER_NAV:
            self.active_input = value
            only_value = False
        else: # encoder_id == _ENCODER_VAL
            active_input = self.active_input
            if active_input == 0: # trigger
                self.trigger = value - 1 # 0 becomes _NONE
            else: # zone
                self.zone = value
            only_value = True
        self.draw(only_value)
        return True

    def button_sel_opt(self) -> bool:
        '''process select button press at pop-up level; called by self.button_yes and ui.process_user_input'''
        self.close()
        if (_callback_func := self._callback_func) is not None:
            _callback_func(self.caller_id, self.trigger, self.zone)
        return True

    def button_yes(self) -> bool:
        '''process confirm button at pop-up level; called by ui.process_user_input'''
        self.button_sel_opt()
        return True

class ChordPopUp(PopUp):
    '''class providing chord select pop-up; initiated once by ui.__init__'''

    def __init__(self, id: int) -> None:
        super().__init__(id)
        self.inside_w = _SELECT_TRIGGER_W
        self.inside_h = 4 * (_POP_UP_LABEL_H + _VALUE_H)

    def open(self, frame, caller_id: int, root: int, octave: int, quality: int, inversion: int, callback_func=None) -> None:
        '''open and draw pop-up and deselect selected page block; called by PageTools.process_user_input'''
        self.caller_id = caller_id
        self.active_input = 0
        self.root = root
        self.octave = octave
        self.quality = quality
        self.inversion = inversion
        self._callback_func = callback_func
        _ui = ml.ui
        _ui.encoder_nav.set(0, 3)
        _ui.encoder_val.set(self.root + 1, len(KEY_OPTIONS) - 1) # _NONE becomes 0
        super().open(frame)

    def draw(self, only_value: bool=False) -> None:
        '''draw pop-up; called by self.open and self.encoder'''
        _ui = ml.ui
        _display = _ui.display
        _rect = _display.rect
        _text = _display.text_box
        active_input = self.active_input
        if only_value:
            if active_input == _CHORD_ROOT:
                value = KEY_OPTIONS[self.root + 1] # _NONE becomes 0
            elif active_input == _CHORD_OCTAVE:
                value = OCTAVE_OPTIONS[self.octave + 2] # _OCTAVE_NONE becomes 0
            elif active_input == _CHORD_QUALITY:
                value = QUALITY_OPTIONS_LONG[self.quality + 1] # _NONE becomes 0
            else: # active_input == _CHORD_INVERSION
                value = INVERSION_OPTIONS[self.inversion]
            y = self.y + _MARGIN_LARGE + active_input * (_POP_UP_LABEL_H + _VALUE_H) + _POP_UP_LABEL_H
            _rect((x := self.x + _MARGIN_LARGE), y, (inside_w := self.inside_w), _VALUE_H, _COLOR_POP_UP_LIGHT, True) # type: ignore (temporary)
            _text(x, y, inside_w, _VALUE_H, value, _COLOR_POP_UP_LIGHT, _COLOR_POP_UP_DARK, _ALIGN_CENTRE)
            return
        if active_input == _CHORD_ROOT:
            _ui.encoder_val.set(self.root + 1, len(KEY_OPTIONS) - 1) # _NONE becomes 0
        elif active_input == _CHORD_OCTAVE:
            _ui.encoder_val.set(self.octave + 2, len(OCTAVE_OPTIONS) - 1) # _OCTAVE_NONE becomes 0
        elif active_input == _CHORD_QUALITY:
            _ui.encoder_val.set(self.quality + 1, len(QUALITY_OPTIONS_LONG) - 1) # _NONE becomes 0
        else: # active_input == _CHORD_INVERSION
            n = 0 if self.quality == _NONE else len(MULTI_CHORDS[self.quality * _MULTI_CHORD_COLUMNS + 2]) - 1
            _ui.encoder_val.set(self.inversion, n)
        self._draw_background()
        x = self.x + _MARGIN_LARGE
        y = self.y + _MARGIN_LARGE
        for i in range(4):
            fore_color = _COLOR_POP_UP_LIGHT if active_input == i else _COLOR_POP_UP_INACTIVE
            if i == _CHORD_ROOT:
                label = 'root'
                value = KEY_OPTIONS[self.root + 1] # _NONE becomes 0
            elif i == _CHORD_OCTAVE:
                label = 'octave'
                value = OCTAVE_OPTIONS[self.octave + 2] # _OCTAVE_NONE becomes 0
            elif i == _CHORD_QUALITY:
                label = 'chord quality'
                value = QUALITY_OPTIONS_LONG[self.quality + 1] # _NONE becomes 0
            else: # i == _CHORD_INVERSION
                label = 'inversion'
                value = INVERSION_OPTIONS[self.inversion]
            _text(x, y, (inside_w := self.inside_w), _POP_UP_LABEL_H, label, _COLOR_POP_UP_DARK, fore_color, _ALIGN_CENTRE)
            y += _POP_UP_LABEL_H
            _rect(x, y, inside_w, _VALUE_H, fore_color, True) # type: ignore (temporary)
            _text(x, y, inside_w, _VALUE_H, value, fore_color, _COLOR_POP_UP_DARK, _ALIGN_CENTRE)
            y += _VALUE_H

    def encoder(self, encoder_id: int, value: int) -> bool:
        '''process value encoder input at pop-up level (ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by ui.process_encoder_input'''
        if encoder_id == _ENCODER_NAV:
            self.active_input = value
            only_value = False
        else: # encoder_id == _ENCODER_VAL
            active_input = self.active_input
            if active_input == _CHORD_ROOT:
                self.root = value - 1 # 0 becomes _NONE
            elif active_input == _CHORD_OCTAVE:
                self.octave = value - 2 # 0 becomes _OCTAVE_NONE
            elif active_input == _CHORD_QUALITY:
                self.quality = value - 1 # 0 becomes _NONE
                self.inversion = 0
            else: # active_input == _CHORD_INVERSION
                self.inversion = value
            only_value = active_input != _CHORD_QUALITY
        self.draw(only_value)
        return True

    def button_sel_opt(self) -> bool:
        '''process select button press at pop-up level; called by self.button_yes and ui.process_user_input'''
        if self.root == _NONE or self.octave == _OCTAVE_NONE or self.quality == _NONE:
            return False
        self.close()
        if (_callback_func := self._callback_func) is not None:
            _callback_func(self.caller_id, self.root, self.octave, self.quality, self.inversion)
        return True

    def button_yes(self) -> bool:
        '''process confirm button at pop-up level; called by ui.process_user_input'''
        return self.button_sel_opt()

class AboutPopUp(PopUp):
    '''class providing about pop-up; initiated once by ui.__init__'''

    def __init__(self, id: int) -> None:
        super().__init__(id)
        self.inside_w = _CONFIRM_W
        self.inside_h = 4 * _CONTROL_H
        self.selection = 0

    def draw(self) -> None:
        '''draw pop-up; called by self.open and self.encoder'''
        _text = ml.ui.display.text_box
        self._draw_background()
        x = self.x + _MARGIN_LARGE
        y = self.y + _MARGIN_LARGE
        _text(x, y, self.inside_w, _CONTROL_H, 'Cybo-Drummer', _COLOR_POP_UP_DARK, _COLOR_POP_UP_LIGHT, _ALIGN_CENTRE)
        y += _CONTROL_H
        _text(x, y, self.inside_w, _CONTROL_H, f'version {_VERSION}', _COLOR_POP_UP_DARK, _COLOR_POP_UP_LIGHT, _ALIGN_CENTRE)
        y += _CONTROL_H
        _text(x, y, self.inside_w, _CONTROL_H, f'(c) 2024-{_YEAR}', _COLOR_POP_UP_DARK, _COLOR_POP_UP_LIGHT, _ALIGN_CENTRE)
        y += _CONTROL_H
        _text(x, y, self.inside_w, _CONTROL_H, 'Harm Lammers', _COLOR_POP_UP_DARK, _COLOR_POP_UP_LIGHT, _ALIGN_CENTRE)

    def button_sel_opt(self) -> bool:
        '''process select button press at pop-up level; called by *PopUp.button_yes and ui.process_user_input'''
        self.close()
        return True

    def button_del(self) -> bool:
        '''process backspace button press at pop-up level; called by Page.process_user_input'''
        self.close()
        return True