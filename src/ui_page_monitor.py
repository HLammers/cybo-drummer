''' Library providing monitor pages class for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024-2025 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

_INITIAL_SUB_PAGE = const(0)

from collections import deque

import main_loops as ml
from ui_pages import Page
from ui_blocks import TitleBar, TextRow

_NONE              = const(-1)

_COLOR_DARK        = const(0xAA29) # 0x29AA dark purple blue
_COLOR_LIGHT       = const(0xD9CD) # 0xCDD9 light purple grey

_PAGE_W            = const(204) # _DISPLAY_W - _PAGES_W
_PAGE_H            = const(163) # _DISPLAY_H - _TITLE_BAR_H
_TITLE_BAR_H       = const(13)
_ROW_H             = const(13)
_MAX_ROWS          = const(12) # int(_PAGE_H / _ROW_H)
_TOP_MARGIN        = const(3) # int((_PAGE_H - _MAX_ROWS * _ROW_H) / 2)

_SUB_PAGES         = const(3)
_SUB_PAGE_ROUTING  = const(0)
_SUB_PAGE_MIDI_IN  = const(1)
# _SUB_PAGE_MIDI_OUT = const(2)

_SELECT_SUB_PAGE   = const(-1)

class PageMonitor(Page):
    '''monitor page class; initiated once by ui.__init__'''

    def __init__(self, id: int, x: int, y: int, w: int, h: int, visible: bool) -> None:
        super().__init__(id, x, y, w, h, _SUB_PAGES, visible)
        self.sub_page = _INITIAL_SUB_PAGE
        self.block_active = True
        self.font_type = None
        self.text_deques = [deque((), _MAX_ROWS - 1), deque((), _MAX_ROWS - 1), deque((), _MAX_ROWS - 1)]
        self.page_is_built = False
        self._build_page()

    def program_change(self, update_only: bool) -> None:
        '''update page after program change; called by ui.program_change'''
        if self.visible:
            self._load()

    def process_user_input(self, id: int, value: int|str = _NONE, button_del: bool = False, button_sel_opt: bool = False) -> bool:
        '''process user input at page level (ui.set_user_input_tuple > ui.user_input_tuple > ui.process_user_input >
        Page/PagesTab.process_user_input); called by ui.process_user_input'''
        value = int(value)
        if id == _SELECT_SUB_PAGE:
            if button_del or button_sel_opt or value == _NONE or value == self.sub_page:
                return False
            self._set_sub_page(value)
            self._reset_monitor()
            self._load()
            return True
        return False

    def add_to_monitor(self, type: int, text: str) -> bool:
        '''add event to monitor deque (router.send_to_monitor > router.monitor_data > ui.process_monitor > PageMonitor.add_to_monitor); called
        by ui.process_monitor'''
        if not self.visible or self.sub_page != type:
            return False
        self.text_deques[type].append(text)
        self._load()
        return True

    def _build_page(self) -> None:
        '''build page (without drawing it); called by self.__init__'''
        if self.page_is_built:
            return
        self.page_is_built = True
        sub_pages_title_bars = self.sub_pages_title_bars
        sub_pages_empty_blocks = self.sub_pages_empty_blocks
        text_deques = self.text_deques
        for i in range(_SUB_PAGES):
            if i == _SUB_PAGE_ROUTING:
                sub_pages_title_bars.append(TitleBar('monitor routing', 1, _SUB_PAGES))
            elif i == _SUB_PAGE_MIDI_IN:
                sub_pages_title_bars.append(TitleBar('monitor midi in', 2, _SUB_PAGES))
            else: # i == _SUB_PAGE_MIDI_OUT
                sub_pages_title_bars.append(TitleBar('monitor midi out', 3, _SUB_PAGES))
            sub_pages_empty_blocks.append((_Monitor(i, text_deques[i]),))
        self.sub_pages_blocks = ((), (), ())
        self._set_sub_page(self.sub_page)

    def _load(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks; called by self.set_visibility, Page*.program_change, Page*.process_user_input,
        PageMonitor.add_to_monitor'''
        if redraw:
            self.draw()

    def _reset_monitor(self):
        '''empty monitor deques; called by self.process_user_input'''
        text_deques = self.text_deques
        for i in range(3):
            while len(text_deques[i]) > 0:
                text_deques[i].pop()

class _Monitor():
    '''class providing the monitor part of a monitor sup-page; initiated by PageMonitor._build_page'''

    def __init__(self, id: int, text_deque: deque) -> None:
        self.id = id
        self.text_deque = text_deque
        self.text_rows = [TextRow(_TITLE_BAR_H + _TOP_MARGIN + i * _ROW_H, _ROW_H, _COLOR_DARK, _COLOR_LIGHT) for i in range(_MAX_ROWS)]

    def draw(self) -> None:
        '''draw monitor part of monitor sub-page; called by PageMonitor._draw'''
        _rect = ml.ui.display.rect
        _rect(0, _TITLE_BAR_H, _PAGE_W, _TOP_MARGIN, _COLOR_DARK, True) # type: ignore (temporary)
        i = -1
        for i, text in enumerate(self.text_deque): # type: ignore (temporary)
            self.text_rows[i].set_text(text, True)
        self.text_rows[i + 1].set_text('...', True)
        h = _PAGE_H - (y := _TITLE_BAR_H + _TOP_MARGIN + (i + 2) * _ROW_H) + _TITLE_BAR_H
        if h > 0:
            _rect(0, y, _PAGE_W, h, _COLOR_DARK, True) # type: ignore (temporary)