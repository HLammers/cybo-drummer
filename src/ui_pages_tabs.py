''' Library providing page select tabs class for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024-2025 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

import main_loops as ml
from ui_blocks import PageTabs
from constants import PAGE_LABELS, MAIN_FRAMES

_NONE = const(-1)

class PagesTabs():
    '''ui pages tab frame class; initiated once by ui.__init__'''

    def __init__(self, id: int, x: int, y: int, w: int, h: int, initial_page: int) -> None:
        self.id = id
        self.pages_tab = PageTabs(x, y, w, h, PAGE_LABELS, MAIN_FRAMES.index(initial_page))

    def set_page_encoders(self, page_pressed: bool) -> None:
        '''switches value encoder input to or from page selection and changes colour of title bar (when page button is pressed); called by
        ui.process_user_input'''
        self.pages_tab.update(page_pressed)

    def program_change(self, update_only: bool) -> None:
        '''update page after program change (needed to trigger draw); called by ui.program_change'''
        self.pages_tab.draw()

    def set_page(self, value: int) -> None:
        '''set, initiate and draw active page (ui.process_encoder > Page/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by ui.process_encoder_input'''
        self.selection = value
        self.pages_tab.encoder(value)
        self.callback_input(self.id, value)
        _ui = ml.ui
        frames = _ui.frames
        frames[_ui.active_frame].set_visibility(False)
        value += 1 # increase with one because the first frame (before the pages) is the pages tab
        _ui.active_frame = value
        frames[value].set_visibility(True)

    def process_user_input(self, id: int, value: int|str = _NONE, button_del: bool = False, button_sel_opt: bool = False) -> bool:
        '''process user input at pages tab level (ui.set_user_input_tuple > ui.user_input_tuple > ui.process_user_input >
        Page/PagesTab.process_user_input); called by ui.process_user_input'''
        return False

    def callback_input(self, id: int, value: int|str = _NONE, button_del: bool = False, button_sel_opt: bool = False) -> None:
        '''callback function for encoder input and blocks offering user input (ui._callback_button/Page/PagesTab.callback_input >
        ui.set_user_input_tuple > ui.user_input_tuple > ui.process_user_input > Page/PagesTab.process_user_input); called (passed on)
        by self.encoder'''
        ml.ui.set_user_input_tuple((self.id, id, value, button_del, button_sel_opt))