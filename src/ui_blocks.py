''' UI building blocks library for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

import framebuf
import time

import ui
if __debug__: import screen_log

_VERSION               = '0.1.0'
_YEAR                  = const(2024)

_ALIGN_LEFT            = const(0)
_ALIGN_CENTRE          = const(1)
_ALIGN_RIGHT           = const(2)

_COLOR_TABS_DARK       = const(0xAA29) # 0x29AA dark purple blue
_COLOR_TABS_LIGHT      = const(0xD095) # 0x95D0 green
_COLOR_TITLE_BACK      = const(0x06ED) # 0xED06 orange
_COLOR_TITLE_FORE      = const(0xAA29) # 0x29AA dark purple blue
_COLOR_BLOCK_DARK      = const(0xAA29) # 0x29AA dark purple blue
_COLOR_BLOCK_LIGHT     = const(0xD9CD) # 0xCDD9 light purple grey
_COLOR_SELECTED_DARK   = const(0x8E33) # 0x338E dark sea green
_COLOR_SELECTED_LIGHT  = const(0xFD97) # 0x97FD light sea green
_COLOR_LINE            = const(0x06ED) # 0xED06 orange
_COLOR_POP_UP_DARK     = const(0x8E33) # 0x338E dark sea green
_COLOR_POP_UP_LIGHT    = const(0xFD97) # 0x97FD light sea green

_MARGIN                = const(3)
_MARGIN_LARGE          = const(10)
_TAB_H                 = const(36) # (h + len(_PAGE_LABELS)) // len(_PAGE_LABELS)
_TITLE_BAR_W           = const(204)
_TITLE_BAR_H           = const(14)
_PROGRAM_NUMBER_W      = const(25)
_BLOCK_H               = const(27)
_BLOCK_W               = const(102)
_LABEL_H               = const(10)
_VALUE_H               = const(17)
_BUTTON_MARGIN_X       = const(20)
_BUTTON_MARGIN_Y       = const(4)
_TEXT_H                = const(15)
_CURSOR_H              = const(10)
_CHAR_W                = const(13)
_CHAR_H                = const(11)
_CONTROL_H             = const(16)
_SELECT_TRIGGER_W      = const(160)
_MENU_W                = const(102)
_CONFIRM_W             = const(102)

_TEXT_INPUT_CHARACTERS = '''ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#%^&*()_-+=[]\\{}|:;"',./<>?'''
_CHARACTER_COLUMNS     = const(13)
_TEXT_INPUT_SPACE_BAR  = 'space bar'

_bit_buffer = memoryview(bytearray(3048)) # large enough for text edit)

class Block():
    '''base class for ui blocks'''

    def __init__(self, id: int, row: int, col: int, cols: int, selected: bool, label: str, add_line: bool = False) -> None:
        self.id = id
        if __debug__:
            self.row = row
            self.col = col
        self.x = col * _BLOCK_W
        self.y = _TITLE_BAR_H + row * _BLOCK_H
        self.w = cols * _BLOCK_W
        self.h = _BLOCK_H
        self.selected = selected
        self.label = label
        self.add_line = add_line
        self.font = ui.display.font

    def update(self, selected: bool, redraw: bool = True, encoder_nr: int = 1) -> None:
        '''update block, set selection state and redraw if necessary; called by PopUp.open, PopUp.close, ui.process_user_input,
        Page.set_visibility, Page.restore, Page.set_page_encoders, Page.encoder, Page._draw, Page._sub_page_selector
        and Page*.program_change'''
        pass

    def draw(self, suppress_selected: bool, only_value: bool, frame_buffer) -> None:
        '''draw whole block or only value part of block; called by PagesTabs.update, TitleBar.update, *Block.update, PagesTabs.encoder
        ButtonBlock.button_select, SelectBlock.set_label, SelectBlock.set_options, Page._draw, _Monitor.draw, Page.restore, Page*._load,
        and PageProgram._save_*_settings'''
        if __debug__: screen_log.add_marker(f'add block {self.row},{self.col}, selected: {self.selected and not suppress_selected}')
        if self.selected and not suppress_selected:
            color_dark = _COLOR_SELECTED_DARK
            color_light = _COLOR_SELECTED_LIGHT
        else:
            color_dark = _COLOR_BLOCK_DARK
            color_light = _COLOR_BLOCK_LIGHT
        if only_value:
            y = self.y + _LABEL_H
            h = _VALUE_H
        else:
            y = self.y
            h = _BLOCK_H
        if self.add_line:
            h -= 2
        ui.scr.draw_frame_buffer(self.x, y, self.w, h, color_dark, color_light, frame_buffer)

    def encoder(self, value: int) -> None:
        '''process value encoder input at block level (ui._callback_encoder_0/_callback_encoder_1 > global encoder_input_0/encoder_input_1 >
        ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder); called by Pages.encoder and PagesTabs.encoder'''
        pass

    def button_select(self) -> None:
        '''process select button press at block level; called by Page.button_select'''
        pass

    def button_backspace(self) -> None:
        '''process backspace button press at block level; called by Page.button_backspace'''
        pass

class PageTabs(Block):
    '''class providing page tabs block for ui; initiated once by PagesTabs.__init__'''

    def __init__(self, x: int, y: int, w: int, h: int, options: list | tuple, selection: int = 0) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.options = options
        self.selection = selection
        self.selected = False
        self.font = ui.display.font

    def update(self, selected, redraw: bool = True):
        '''update block, set selection state and redraw if necessary; called by PageTab.set_page_encoders'''
        self.selected = selected
        if selected:
            ui.encoder_1.set(self.selection, 0, len(self.options) - 1)
        if redraw:
            self.draw()

    def draw(self):
        '''draw whole block or only value part of block; called by PagesTabs.update, PagesTabs.encoder and PagesTabs.draw'''
        if __debug__: screen_log.add_marker(f'add tabs, selected: {self.selected}')
        if self.selected:
            back_color = _COLOR_SELECTED_DARK
            fore_color = _COLOR_SELECTED_LIGHT
        else:
            back_color = _COLOR_TABS_DARK
            fore_color = _COLOR_TABS_LIGHT
        w = self.w
        h = self.h
        options = self.options
        selection = self.selection
        _buffer = framebuf.FrameBuffer(_bit_buffer, w, h, framebuf.MONO_HMSB)
        _buffer.fill(0)
        _rect = _buffer.rect
        _text = self.font.vertical_text_box
        for i in range(len(options)):
            y = i * (_TAB_H - 1)
            if i == selection:
                _rect(0, y, w, _TAB_H, True, True)
                color = 0
            else:
                color = 1
            _text(0, y, w, _TAB_H, options[i], color, _ALIGN_CENTRE, _buffer)
        ui.scr.draw_frame_buffer(self.x, self.y, w, h, back_color, fore_color, _buffer)

    def encoder(self, value: int) -> bool:
        '''process value encoder input at block level (ui._callback_encoder_0/_callback_encoder_1 > global encoder_input_0/encoder_input_1 >
        ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder); called by PagesTabs.encoder'''
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
        self.w = _TITLE_BAR_W
        self.h = _TITLE_BAR_H
        self.font = ui.display.font

    def update(self, selected, redraw: bool = True):
        '''update block, set selection state and redraw if necessary; called by Page._draw and Page._sub_page_selector'''
        self.selected = selected
        if selected:
            ui.encoder_0.set(self.page_number - 1, 0, self.number_of_pages - 1)
        if redraw:
            self.draw()

    def draw(self):
        '''draw whole block or only value part of block; called by TitleBar.update, Page.restore and Page._draw'''
        if __debug__: screen_log.add_marker(f'add title bar ‘{self.title}’,{self.page_number}/{self.number_of_pages}, selected: {self.selected}')
        if self.selected:
            back_color = _COLOR_SELECTED_LIGHT
            fore_color = _COLOR_SELECTED_DARK
        else:
            back_color = _COLOR_TITLE_BACK
            fore_color = _COLOR_TITLE_FORE
        _router = ui.router
        program = f'{_router.active_program_number + 1:0>3}'
        if _router.program_changed:
            program += '*'
        page = f'{self.page_number}/{self.number_of_pages}'
        _buffer = framebuf.FrameBuffer(_bit_buffer, _TITLE_BAR_W, _TITLE_BAR_H, framebuf.MONO_HMSB)
        _buffer.fill(0)
        _text = self.font.text_box
        _text(_MARGIN, 0, _PROGRAM_NUMBER_W, _TITLE_BAR_H, program, 1, _ALIGN_LEFT, _buffer)
        _text(_PROGRAM_NUMBER_W + _MARGIN, 0, _TITLE_BAR_W - 2 * _PROGRAM_NUMBER_W - 2 * _MARGIN, _TITLE_BAR_H, self.title, 1, _ALIGN_CENTRE,
              _buffer)
        _text(_TITLE_BAR_W - _PROGRAM_NUMBER_W - _MARGIN, 0, _PROGRAM_NUMBER_W, _TITLE_BAR_H, page, 1, _ALIGN_RIGHT, _buffer)
        ui.scr.draw_frame_buffer(0, 0, _TITLE_BAR_W, _TITLE_BAR_H, back_color, fore_color, _buffer)

class EmptyRow():
    '''class providing empty row for ui pages; initiated by Page*._build_sub_page'''

    def __init__(self, id: int, row: int) -> None:
        self.id = id
        if __debug__: self.row = row
        self.y = _TITLE_BAR_H + row * _BLOCK_H
        self.w = 2 * _BLOCK_W

    def draw(self) -> None:
        '''draw whole block or only value part of block; called by Page._draw and Page*._load'''
        if __debug__: screen_log.add_marker(f'add empty row {self.row}')
        ui.scr.fill_rect(0, self.y, self.w, _BLOCK_H, _COLOR_BLOCK_DARK)

class EmptyBlock(Block):
    '''class providing empty block for ui pages; initiated by Page*._build_sub_page'''

    def __init__(self, id: int, row: int, col: int, cols: int, add_line: bool = False) -> None:
        super().__init__(id, row, col, cols, False, '', add_line)

    def draw(self) -> None:
        '''draw whole block or only value part of block; called by Page._draw and Page*._load'''
        if __debug__: screen_log.add_marker(f'add empty block {self.row},{self.col}')
        x = self.x
        y = self.y
        w = self.w
        scr = ui.scr
        scr.fill_rect(x, y, w, _LABEL_H, _COLOR_BLOCK_LIGHT)
        y += _LABEL_H
        if self.add_line:
            scr.fill_rect(x, y, w, _VALUE_H - 2, _COLOR_BLOCK_DARK)
            y += _VALUE_H - 2
            scr.fill_rect(x, y, w, 2, _COLOR_LINE)
        else:
            scr.fill_rect(x, y, w, _VALUE_H, _COLOR_BLOCK_DARK)

class ButtonBlock(Block):
    '''class providing button block for ui pages; initiated by Page*._build_sub_page'''

    def __init__(self, id, row: int, col: int, cols: int, selected: bool, label: str, add_line: bool = False, callback_func=None) -> None:
        super().__init__(id, row, col, cols, selected, label, add_line)
        self.callback_func = callback_func

    def update(self, selected: bool, redraw: bool = True, encoder_nr: int = 1) -> None:
        '''update block, set selection state and redraw if necessary; called by PopUp.open, PopUp.close, ui.process_user_input,
        Page.set_visibility, Page.set_page_encoders, Page.encoder, Page*.program_change and Page._draw'''
        self.selected = selected
        if redraw:
            self.draw()

    def draw(self, suppress_selected: bool = False, pressed: bool = False, only_value: bool = False) -> None:
        '''draw whole block or only value part of block; called by *Block.update, ButtonBlock.button_select and Page._draw'''
        w = self.w
        if only_value:
            _buffer = framebuf.FrameBuffer(_bit_buffer, w, _VALUE_H, framebuf.MONO_HMSB)
            _buffer.fill(0)
            y = _BUTTON_MARGIN_Y
        else:
            _buffer = framebuf.FrameBuffer(_bit_buffer, w, _BLOCK_H, framebuf.MONO_HMSB)
            _buffer.rect(0, 0, w, _LABEL_H, True, True)
            self.font.text_box(0, 0, w, _LABEL_H, self.label, 0, _ALIGN_CENTRE, _buffer)
            _buffer.rect(0, _LABEL_H, w, _VALUE_H, False, True)
            y = _LABEL_H + _BUTTON_MARGIN_Y
        _buffer.rect(_BUTTON_MARGIN_X, y, w - 2 * _BUTTON_MARGIN_X, _VALUE_H - 2 * _BUTTON_MARGIN_Y, True, False)
        if not pressed:
            _buffer.rect(_BUTTON_MARGIN_X + 2, y + 2, w - 2 * _BUTTON_MARGIN_X - 5, _VALUE_H - 2 * _BUTTON_MARGIN_Y - 5, True, True)
        super().draw(suppress_selected, only_value, _buffer)
        if self.add_line:
            ui.scr.fill_rect(self.x, self.y + _BLOCK_H - 2, w, 2, _COLOR_LINE)

    def button_select(self) -> None:
        '''process select button press at block level; called by Page.button_select'''
        if not self.selected or self.callback_func is None:
            return
        self.draw(pressed=True)
        time.sleep_ms(300)
        self.draw()
        self.callback_func(self.id, button_encoder_1=True)

class SelectBlock(Block):
    '''class providing value select block for ui pages; initiated by Page*._build_sub_page'''

    def __init__(self, id, row: int, col: int, cols: int, selected: bool, label: str, options = (),
                 selection: int = 0, add_line: bool = False, callback_func=None) -> None:
        super().__init__(id, row, col, cols, selected, label, add_line)
        self.options = options
        self.selection = selection
        self.callback_func = callback_func

    def update(self, selected: bool, redraw: bool = True, encoder_nr: int = 1) -> None:
        '''update block, set selection state and redraw if necessary; called by PopUp.open, PopUp.close, ui.process_user_input,
        Page.set_visibility, Page.set_page_encoders, Page.encoder and Page*.program_change and Page._draw'''
        self.selected = selected
        if selected:
            encoder = ui.encoder_0 if encoder_nr == 0 else ui.encoder_1
            encoder.set(self.selection, 0, len(self.options) - 1)
        if redraw:
            self.draw()

    def draw(self, suppress_selected: bool = False, only_value: bool = False) -> None:
        '''draw whole block or only value part of block; called by *Block.update, SelectBlock.set_label, SelectBlock.set_options and
        Page._draw'''
        w = self.w
        _text = self.font.text_box
        if only_value:
            _buffer = framebuf.FrameBuffer(_bit_buffer, w, _VALUE_H, framebuf.MONO_HMSB)
            _buffer.fill(0)
            y = 1
        else:
            _buffer = framebuf.FrameBuffer(_bit_buffer, w, _BLOCK_H, framebuf.MONO_HMSB)
            _buffer.rect(0, 0, w, _LABEL_H, True, True)
            _text(0, 0, w, _LABEL_H, self.label, 0, _ALIGN_CENTRE, _buffer)
            _buffer.rect(0, _LABEL_H, w, _VALUE_H, False, True)
            y = _LABEL_H + 1
        if self.selection < len(self.options):
            value = self.options[self.selection]
        else:
            value = ''
        w = self.w
        _text(0, y, w, _VALUE_H - 2, value, 1, _ALIGN_CENTRE, _buffer)
        super().draw(suppress_selected, only_value, _buffer)
        if self.add_line:
            ui.scr.fill_rect(self.x, self.y + _BLOCK_H - 2, w, 2, _COLOR_LINE)

    def set_label(self, label: str, redraw: bool = True):
        '''set text for label part of block; called by PagesProgram._set_program_options'''
        self.label = label
        if redraw:
            self.draw()

    def set_options(self, options = None, selection: int = 0, redraw: bool = True) -> int:
        '''set list of options and current selection; called by self.encoder, Pages*._set_*_options and PageSettings.midi_learn'''
        if options is None:
            options = self.options
        else:
            if len(options) == 0:
                options = ('',)
            self.options = options
            if self.selected and not ui.ui.page_pressed:
                ui.encoder_1.set(selection, 0, len(options) - 1)
        if selection >= len(options):
            selection = len(options) - 1
        self.selection = selection
        self.text = str(options[selection])
        if redraw:
            self.draw()
        return selection

    def encoder(self, value: int) -> None:
        '''process value encoder input at block level (ui._callback_encoder_0/_callback_encoder_1 > global encoder_input_0/encoder_input_1 >
        ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder); called by Pages.encoder'''
        if not self.selected or self.callback_func is None:
            return
        value = self.set_options(selection=value)
        self.callback_func(self.id, value, self.options[value])

    def button_select(self) -> None:
        '''process select button press at block level; called by Page.button_select'''
        if not self.selected or self.callback_func is None:
            return
        self.callback_func(self.id, button_encoder_1=True)

    def button_backspace(self) -> None:
        '''process backspace button press at block level; called by Page.button_backspace'''
        if not self.selected or self.callback_func is None:
            return
        self.callback_func(self.id, button_encoder_0=True)

class TextRow():
    '''class providing text row block for monitor page; initiated by _Monitor.draw'''

    def __init__(self) -> None:
        self.font = ui.display.font

    def draw(self, x: int, y: int, w: int, h: int, text: str, back_color: int, fore_color: int) -> None:
        '''draw whole block or only value part of block; called by _Monitor.draw'''
        if __debug__: screen_log.add_marker('add text row')
        self.w = w
        _buffer = framebuf.FrameBuffer(_bit_buffer, w, h, framebuf.MONO_HMSB)
        _buffer.fill(0)
        self.font.text_box(1, 0, w - 2, h, text, 1, _ALIGN_LEFT, _buffer)
        ui.scr.draw_frame_buffer(x, y, w, h, back_color, fore_color, _buffer)

class PopUp():
    '''base class for pop-ups'''

    def __init__(self, id: int) -> None:
        self.id = id
        self.inside_w = 0
        self.inside_h = 0
        self.visible = False
        self.font = ui.display.font

    def open(self, frame) -> None:
        '''open and draw pop-up and deselect selected page block; called by ui.process_user_input, Page*.process_user_input,
        PageProgram._callback_confirm and PageProgram._callback_menu'''
        self.frame = frame
        self.visible = True
        ui.ui.active_pop_up = self # type: ignore
        active_page = ui.ui.frames[ui.ui.active_page]
        if len(active_page.blocks) > 0:
            active_page.blocks[active_page.selected_block].update(False)
        self.w = self.inside_w + 2 * _MARGIN_LARGE
        self.h = self.inside_h + 2 * _MARGIN_LARGE
        self.x = self.frame.x + (self.frame.w - self.w) // 2
        self.y = self.frame.y + (self.frame.h - self.h) // 2
        self.draw()

    def draw(self) -> None:
        '''draw pop-up; called by PopUp.open, SelectPopUp.encoder, MenuPopUp.encoder and Page._draw'''
        pass

    def close(self) -> None:
        '''close pop-up and resselect selected page block; called by self.button_cancel, self.button_confirm, SelectPopUp.button_select,
        MenuPopUp.button_select and ui.process_user_input'''
        ui.ui.active_pop_up = None
        self.visible = False
        active_page = ui.ui.frames[ui.ui.active_page]
        if len(active_page.blocks) > 0:
            active_page.blocks[active_page.selected_block].update(True, False)

    def encoder(self, encoder_nr: int, value: int) -> None:
        '''process encoder input at pop-up level (ui.callback_encoder_0/callback_encoder_1 > global encoder_input_0/encoder_input_1 >
        ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder); called by ui.process_encoder_input'''
        pass

    def button_select(self) -> None:
        '''process select button press at pop-up level; called by SelectPopUp.button_confirm, MenuPopUp.button_confirm and
        ui.process_user_input'''
        pass

    def button_backspace(self) -> None:
        '''process backspace button press at pop-up level; called by Page.process_user_input'''
        pass

    def button_cancel(self) -> bool:
        '''process cancel button at pop-up level; called by ui.process_user_input'''
        self.close()
        return True

    def button_confirm(self) -> bool:
        '''process confirm button at pop-up level; called by ui.process_user_input'''
        self.close()
        return False
        
class TextEdit(PopUp):
    '''class providing text edit pop-up; initiated once by ui.__init__'''

    def __init__(self, id: int) -> None:
        super().__init__(id)
        self.character_rows = -(-len(_TEXT_INPUT_CHARACTERS) // _CHARACTER_COLUMNS)
        self.inside_w = _CHARACTER_COLUMNS * _CHAR_W + 1
        self.inside_h = _TEXT_H + _MARGIN + (self.character_rows + 1) * _CHAR_H + 1
        self.x = 0
        self.y = 0
        self.characters_left = _MARGIN_LARGE
        self.characters_top = _MARGIN_LARGE + _TEXT_H + _MARGIN
        self.input_w = self.inside_w - 2 * _MARGIN
        self.cursor_y = (_TEXT_H - _CURSOR_H) // 2
        self.selection_x = None
        self.selection_y = None

    def open(self, frame, caller_id: int, text: str, max_characters: int = 27, callback_func=None) -> None:
        '''open and draw pop-up and deselect selected page block; called by Page*.process_user_input and PageProgram._callback_menu'''
        self.caller_id = caller_id
        self.text = text
        self.max_characters = max_characters
        self._callback_func = callback_func
        self.selection_x = None
        self.selection_y = None
        super().open(frame)
        self._update_selection(0, 0)
        ui.encoder_0.set(0, 0, self.character_rows)
        ui.encoder_1.set(0, 0, _CHARACTER_COLUMNS - 1)

    def draw(self) -> None:
        '''draw pop-up; called by PopUp.open and Page._draw'''
        if __debug__: screen_log.add_marker(f'draw text edit pop-up')
        inside_w = self.inside_w
        _buffer = framebuf.FrameBuffer(_bit_buffer, self.w, self.h, framebuf.MONO_HMSB)
        _buffer.fill(0)
        _text = self.font.text_box
        _buffer.rect(_MARGIN_LARGE, _MARGIN_LARGE, inside_w, _TEXT_H, True, True)
        for i, ch in enumerate(_TEXT_INPUT_CHARACTERS):
            x = self.characters_left + (i % _CHARACTER_COLUMNS) * _CHAR_W
            y = self.characters_top + (i // _CHARACTER_COLUMNS) * _CHAR_H
            _text(x, y, _CHAR_W, _CHAR_H, ch, 1, _ALIGN_CENTRE, _buffer)
        _text(self.characters_left, self.characters_top + self.character_rows * _CHAR_H, self.input_w, _CHAR_W,
              _TEXT_INPUT_SPACE_BAR, 1, _ALIGN_CENTRE, _buffer)
        ui.scr.draw_frame_buffer(self.x, self.y, self.w, self.h, _COLOR_POP_UP_DARK, _COLOR_POP_UP_LIGHT, _buffer)
        self._draw_input_text()

    def encoder(self, encoder_nr: int, value: int) -> None:
        '''process encoder input at pop-up level (ui._callback_encoder_0/_callback_encoder_1 > global encoder_input_0/encoder_input_1 >
        ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder); called by ui.process_encoder_input'''
        if encoder_nr == 0:
            self._update_selection(selection_y=value)
        else:
            self._update_selection(selection_x=value)

    def button_select(self) -> None:
        '''process select button press at pop-up level; called by ui.process_user_input'''
        if self.selection_x is None or self.selection_y is None:
            return
        if self.selection_y < self.character_rows:
            pos = self.selection_y * _CHARACTER_COLUMNS + self.selection_x
            self.text = self.text + _TEXT_INPUT_CHARACTERS[pos]
        else:
            self.text = self.text + ' '
        self._draw_input_text()

    def button_backspace(self) -> None:
        '''process backspace button press at pop-up level; called by Page.process_user_input'''
        if len(self.text) > 0:
            self.text = self.text[:-1]
            self._draw_input_text()        

    def button_confirm(self) -> bool:
        '''process confirm button at pop-up level; called by ui.process_user_input'''
        self.close()
        try:
            self._callback_func(self.caller_id, self.text) # type: ignore
        except:
            pass
        return True

    def _draw_input_text(self) -> None:
        '''draw or update text being edited; called by self.draw, self.button_select and self.button_backspace'''
        _scr = ui.scr
        x = self.x + _MARGIN_LARGE + _MARGIN
        y = self.y + _MARGIN_LARGE
        input_w = self.input_w
        text = self.text
        _buffer = framebuf.FrameBuffer(_bit_buffer, input_w, _TEXT_H, framebuf.MONO_HMSB)
        _buffer.fill(0)
        _font = self.font
        _font.text_box(0, 0, input_w, _TEXT_H, text, 1, _ALIGN_LEFT, _buffer)
        ui.scr.draw_frame_buffer(x, y, input_w, _TEXT_H, _COLOR_POP_UP_LIGHT, _COLOR_POP_UP_DARK, _buffer)
        x0, y0, tw, th = _font.get_text_box_bounds(x, y, input_w, _TEXT_H, text, _ALIGN_LEFT)
        cursor_x = x0 + tw + 1
        cursor_y = y0 + th - 2
        cursor_w, _ = _font.get_text_bounds('0')
        if len(text) == 0 or text[-1] == ' ':
            w, _ = _font.get_text_bounds('.')
            cursor_x += w
        _scr.fill_rect(cursor_x, cursor_y, cursor_w, 2, _COLOR_POP_UP_DARK)

    def _update_selection(self, selection_x: int | None = None, selection_y: int | None = None) -> None:
        '''update input character (or space bar) selection; called by self.open and self.encoder'''
        self_selection_x = self.selection_x
        self_selection_y = self.selection_y
        x = self_selection_x if selection_x is None else selection_x
        y = self_selection_y if selection_y is None else selection_y
        if (x is None or y is None) or (self_selection_x == x and self_selection_y == y):
            return
        if self_selection_x is not None and self_selection_y is not None:
            self._draw_selection(self_selection_x, self_selection_y, False)
        self._draw_selection(x, y, True)
        self.selection_x = x
        self.selection_y = y

    def _draw_selection(self, selection_x: int, selection_y: int, selected: bool) -> None:
        '''draw input character (or space bar) to be selected on deselected; called by self._update_selection'''
        if selected:
            fore_color = _COLOR_POP_UP_DARK
            back_color = _COLOR_POP_UP_LIGHT
        else:
            fore_color = _COLOR_POP_UP_LIGHT
            back_color = _COLOR_POP_UP_DARK
        y = self.y + self.characters_top + selection_y * _CHAR_H
        if selection_y < self.character_rows:
            pos = selection_y * _CHARACTER_COLUMNS + selection_x
            text = _TEXT_INPUT_CHARACTERS[pos]
            x = self.x + self.characters_left + selection_x * _CHAR_W
            w = _CHAR_W
        else:
            text = _TEXT_INPUT_SPACE_BAR
            x = self.x + self.characters_left
            w = self.input_w
        _buffer = framebuf.FrameBuffer(_bit_buffer, w, _CHAR_H, framebuf.MONO_HMSB)
        _buffer.fill(0)
        self.font.text_box(0, 0, w, _CHAR_H, text, 1, _ALIGN_CENTRE, _buffer)
        ui.scr.draw_frame_buffer(x, y, w, _CHAR_H, back_color, fore_color, _buffer)

class SelectPopUp(PopUp):
    '''class providing value select pop-up; initiated once by ui.__init__'''

    def __init__(self, id: int) -> None:
        super().__init__(id)
        self.inside_w = _SELECT_TRIGGER_W
        self.inside_h = _LABEL_H + _VALUE_H

    def open(self, frame, caller_id: int, label: str, options: list|tuple, selection: int, instant: bool = False, callback_func=None) -> None:
        '''open and draw pop-up and deselect selected page block; called by ui.process_user_input, Page*.process_user_input and
        PageProgram._callback_menu'''
        self.caller_id = caller_id
        self.label = label
        self.options = options
        self.selection = selection
        self.instant = instant
        self._callback_func = callback_func
        super().open(frame)

    def draw(self, only_value: bool=False) -> None:
        '''draw pop-up; called by PopUp.open and SelectPopUp.encoder'''
        if __debug__: screen_log.add_marker(f'draw select pop-up')
        ui.encoder_1.set(self.selection, 0, len(self.options) - 1)
        value = '' if len(self.options) == 0 else self.options[self.selection]
        self.value = value
        inside_w = self.inside_w
        if only_value:
            _buffer = framebuf.FrameBuffer(_bit_buffer, inside_w, _VALUE_H, framebuf.MONO_HMSB)
            _buffer.fill(0)
            self.font.text_box(0, 0, inside_w, _VALUE_H, value, 1, _ALIGN_CENTRE, _buffer)
            x = self.x + _MARGIN_LARGE
            y = self.y + _MARGIN_LARGE + _LABEL_H
            w = inside_w
            h = _VALUE_H
            back_color = _COLOR_POP_UP_LIGHT
            fore_color = _COLOR_POP_UP_DARK
        else:
            _buffer = framebuf.FrameBuffer(_bit_buffer, self.w, self.h, framebuf.MONO_HMSB)
            _buffer.fill(0)
            _text = self.font.text_box
            _text(_MARGIN_LARGE, _MARGIN_LARGE, inside_w, _LABEL_H, self.label, 1, _ALIGN_CENTRE, _buffer)
            _buffer.rect(_MARGIN_LARGE, _MARGIN_LARGE + _LABEL_H, inside_w, _VALUE_H, True, True)
            _text(_MARGIN_LARGE, _MARGIN_LARGE + _LABEL_H, inside_w, _VALUE_H, value, 0, _ALIGN_CENTRE, _buffer)
            x = self.x
            y = self.y
            w = self.w
            h = self.h
            back_color = _COLOR_POP_UP_DARK
            fore_color = _COLOR_POP_UP_LIGHT
        ui.scr.draw_frame_buffer(x, y, w, h, back_color, fore_color, _buffer)

    def encoder(self, encoder_nr: int, value: int) -> None:
        '''process value encoder input at pop-up level (ui._callback_encoder_0/_callback_encoder_1 > global encoder_input_0/encoder_input_1 >
        ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder); called by ui.process_encoder_input'''
        if encoder_nr != 1:
            return
        self.selection = value
        self.draw(True)
        if not self.instant:
            return
        try:
            self._callback_func(self.caller_id, self.selection) # type: ignore
        except:
            pass

    def button_cancel(self) -> bool:
        '''process cancel button at pop-up level; called by ui.process_user_input'''
        if self.instant:
            return False
        self.close()
        return True

    def button_select(self) -> None:
        '''process select button press at pop-up level; called by SelectPopUp.button_confirm and ui.process_user_input'''
        if self.instant:
            return
        self.close()
        try:
            self._callback_func(self.caller_id, self.selection) # type: ignore
        except:
            pass

    def button_confirm(self) -> bool:
        '''process confirm button at pop-up level; called by ui.process_user_input'''
        self.button_select()
        return True

class MenuPopUp(PopUp):
    '''class providing menu pop-up; initiated once by ui.__init__'''

    def __init__(self, id: int) -> None:
        super().__init__(id)
        self.inside_w = _MENU_W
        self.selection = 0

    def open(self, frame, caller_id: int, options: tuple, selection: int = 0, callback_func=None) -> None:
        '''open and draw pop-up and deselect selected page block; called by Page*.process_user_input'''
        self.caller_id = caller_id
        self.options = options
        self.selection = selection
        self._callback_func = callback_func
        self.inside_h = len(options) * _CONTROL_H
        super().open(frame)

    def draw(self) -> None:
        '''draw pop-up; called by PopUp.open and SelectPopUp.encoder'''
        if __debug__: screen_log.add_marker(f'draw menu pop-up')
        _buffer = framebuf.FrameBuffer(_bit_buffer, self.w, self.h, framebuf.MONO_HMSB)
        _buffer.fill(0)
        x = _MARGIN_LARGE
        y = _MARGIN_LARGE
        inside_w = self.inside_w
        text_w = inside_w - 2 * _MARGIN
        options = self.options
        selection = self.selection
        ui.encoder_1.set(selection, 0, len(options) - 1)
        _rect = _buffer.rect
        _text = self.font.text_box
        for i, option in enumerate(options):
            if i == selection:
                _rect(x, y, inside_w, _CONTROL_H, True, True)
                color = 0
            else:
                color = 1
            _text(x + _MARGIN, y, text_w, _CONTROL_H, option, color, _ALIGN_CENTRE, _buffer)
            y += _CONTROL_H
        ui.scr.draw_frame_buffer(self.x, self.y, self.w, self.h, _COLOR_POP_UP_DARK, _COLOR_POP_UP_LIGHT, _buffer)

    def encoder(self, encoder_nr: int, value: int) -> None:
        '''process value encoder input at pop-up level (ui._callback_encoder_0/_callback_encoder_1 > global encoder_input_0/encoder_input_1 >
        ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder); called by ui.process_encoder_input'''
        if encoder_nr != 1:
            return
        self.selection = value
        self.draw()

    def button_select(self) -> None:
        '''process select button press at pop-up level; called by MenuPopUp.button_confirm and ui.process_user_input'''
        self.close()
        try:
            self._callback_func(self.caller_id, self.selection) # type: ignore
        except:
            pass

    def button_cancel(self) -> bool:
        '''process cancel button at pop-up level; called by ui.process_user_input'''
        self.close()
        return True

    def button_confirm(self) -> bool:
        '''process confirm button at pop-up level; called by ui.process_user_input'''
        self.button_select()
        return True

class ConfirmPopUp(PopUp):
    '''class providing confirmation pop-up; initiated once by ui.__init__'''

    def __init__(self, id: int) -> None:
        super().__init__(id)
        self.inside_w = _CONFIRM_W
        self.inside_h = _CONTROL_H
        self.selection = 0

    def open(self, frame, caller_id: int, label, callback_func=None) -> None:
        '''open and draw pop-up and deselect selected page block; called by Page*.process_user_input, PageProgram._callback_confirm and
        PageProgram._callback_menu'''
        self.caller_id = caller_id
        self.label = label
        self._callback_func = callback_func
        super().open(frame)

    def draw(self) -> None:
        '''draw pop-up; called by PopUp.open and *PopUp.encoder'''
        if __debug__: screen_log.add_marker(f'draw confirm pop-up')
        _buffer = framebuf.FrameBuffer(_bit_buffer, self.w, self.h, framebuf.MONO_HMSB)
        _buffer.fill(0)
        self.font.text_box(_MARGIN_LARGE, _MARGIN_LARGE, self.inside_w, _CONTROL_H, self.label, 1, _ALIGN_CENTRE, _buffer)
        ui.scr.draw_frame_buffer(self.x, self.y, self.w, self.h, _COLOR_POP_UP_DARK, _COLOR_POP_UP_LIGHT, _buffer)

    def button_cancel(self) -> bool:
        '''process cancel button at pop-up level; called by ui.process_user_input'''
        self.close()
        try:
            self._callback_func(self.caller_id, False) # type: ignore
        except:
            pass
        return True

    def button_confirm(self) -> bool:
        '''process confirm button at pop-up level; called by ui.process_user_input'''
        self.close()
        try:
            self._callback_func(self.caller_id, True) # type: ignore
        except:
            pass
        return True

class AboutPopUp(PopUp):
    '''class providing about pop-up; initiated once by ui.__init__'''

    def __init__(self, id: int) -> None:
        super().__init__(id)
        self.inside_w = _CONFIRM_W
        self.inside_h = 4 * _CONTROL_H
        self.selection = 0

    def open(self, frame, caller_id: int) -> None:
        '''open and draw pop-up and deselect selected page block; called by Page*.process_user_input, PageProgram._callback_confirm and
        PageProgram._callback_menu'''
        self.caller_id = caller_id
        super().open(frame)

    def draw(self) -> None:
        '''draw pop-up; called by PopUp.open and *PopUp.encoder'''
        if __debug__: screen_log.add_marker(f'draw about pop-up')
        _buffer = framebuf.FrameBuffer(_bit_buffer, self.w, self.h, framebuf.MONO_HMSB)
        _buffer.fill(0)
        y = _MARGIN_LARGE
        self.font.text_box(_MARGIN_LARGE, y, self.inside_w, _CONTROL_H, 'Cybo-Drummer', 1, _ALIGN_CENTRE, _buffer)
        y += _CONTROL_H
        self.font.text_box(_MARGIN_LARGE, y, self.inside_w, _CONTROL_H, f'version {_VERSION}', 1, _ALIGN_CENTRE, _buffer)
        y += _CONTROL_H
        self.font.text_box(_MARGIN_LARGE, y, self.inside_w, _CONTROL_H, f'(c) {_YEAR}', 1, _ALIGN_CENTRE, _buffer)
        y += _CONTROL_H
        self.font.text_box(_MARGIN_LARGE, y, self.inside_w, _CONTROL_H, 'Harm Lammers', 1, _ALIGN_CENTRE, _buffer)
        ui.scr.draw_frame_buffer(self.x, self.y, self.w, self.h, _COLOR_POP_UP_DARK, _COLOR_POP_UP_LIGHT, _buffer)

    def button_cancel(self) -> bool:
        '''process cancel button at pop-up level; called by ui.process_user_input'''
        self.close()
        return True

    def button_confirm(self) -> bool:
        '''process confirm button at pop-up level; called by ui.process_user_input'''
        self.close()
        return True