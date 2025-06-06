''' Library providing base UI page class for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024-2025 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

import main_loops as ml

_NONE             = const(-1)

# _ENCODER_NAV      = const(0)
_ENCODER_VAL      = const(1)

_POP_UP_TEXT_EDIT = const(0)

_SELECT_SUB_PAGE  = const(-1)

class Page():
    '''ui page base class'''

    def __init__(self, id: int, x: int, y: int, w: int, h: int, sub_pages: int, visible: bool) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.visible = visible
        self.sub_page = 0
        self.selected_block = [0] * sub_pages
        self.sub_pages_blocks = []
        self.sub_pages_empty_blocks = []
        self.sub_pages_title_bars = []
        self.sub_pages_text_rows = []
        self.sub_page = 0
        self.tite_bar = None
        self.blocks = []
        self.empty_blocks = []

    def set_visibility(self, visible: bool) -> None:
        '''set the visibility of a page, set the sub-page and set block selection; called by PagesTab.set_page'''
        if visible == self.visible:
            return
        if visible:
            self.visible = visible
            blocks = self.blocks
            if ml.ui.page_select_mode:
                self._sub_page_selector(False)
            elif len(blocks) > 0:
                blocks[0].update(True, False)
            self._load()
        else:
            self.visible = visible

    def draw(self) -> None:
        '''draw whole page; called by self.restore, ui._callback_*, Page*._load and Page*._callback_*'''
        _ui = ml.ui
        if not self.visible or _ui.active_pop_up is not None:
            return
        page_select_mode = _ui.page_select_mode
        selected_block = self.selected_block[self.sub_page]
        if len(blocks := self.blocks) > 0:
            blocks[selected_block].update(not page_select_mode, False)
        for block in self.empty_blocks:
            block.draw()
        for block in blocks:
            block.draw(page_select_mode)
        self.title_bar.update(page_select_mode)
        if self.text_row is not None:
            self.text_row.draw()
        _text_edit = _ui.pop_ups[_POP_UP_TEXT_EDIT]
        if _text_edit.visible:
            _text_edit.draw()
        elif not page_select_mode:
            self._initiate_nav_encoder(selected_block)

    def program_change(self, update_only: bool) -> None:
        '''update page after program change (also needed to trigger draw); called by ui.program_change'''
        pass

    def restore(self):
        '''redraw blocks on page; called by ui.process_user_input'''
        self.title_bar.draw()
        if len(blocks := self.blocks) > 0:
            blocks[self.selected_block[self.sub_page]].update(True, False)
        self.draw()

    def set_page_encoders(self, page_select_mode: bool) -> None:
        '''switches value encoder input to or from page selection and changes colour of title bar (when page button is pressed); called by
        ui.process_user_input'''
        blocks = self.blocks
        if page_select_mode:
            if len(blocks) > 0:
                blocks[self.selected_block[self.sub_page]].update(False)
            self._sub_page_selector()
        else:
            self.title_bar.update(False)
            if len(blocks) > 0:
                blocks[(selected_block := self.selected_block[self.sub_page])].update(True, encoder_id=_ENCODER_VAL)
                self._initiate_nav_encoder(selected_block)

    def encoder(self, encoder_id: int, value: int, page_select_mode: bool) -> bool:
        '''process encoder input at page level (ui.process_encoder > Page.encoder/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by ui.process_encoder_input'''
        if page_select_mode:
            if len(self.sub_pages_blocks) > 1:
                self.callback_input(_SELECT_SUB_PAGE, value)
            return False
        if len(blocks := self.blocks) == 0:
            return False
        selected_block = self.selected_block[self.sub_page]
        if encoder_id == _ENCODER_VAL:
            return blocks[selected_block].encoder(value)
        # encoder_id == _ENCODER_NAV
        n = len(blocks)
        step = -1 if value < selected_block or value == n - 1 else 1
        new_value = value
        while new_value != selected_block and not blocks[new_value].enabled:
            new_value += step
            if new_value == -1:
                new_value = n - 1
            elif new_value == n:
                new_value = 0
        if new_value == selected_block:
            return False
        blocks[selected_block].update(False)
        self.selected_block[self.sub_page] = new_value
        blocks[new_value].update(True)
        if new_value != value:
            ml.ui.encoder_nav.set(new_value)
        return True

    def button_del(self, press_state: int) -> bool:
        '''process backspace button press at page level; called by ui.process_user_input'''
        return self.blocks[self.selected_block[self.sub_page]].button_del()

    def button_sel_opt(self, press_state: int) -> bool:
        '''process select button press at page level; called by ui.process_user_input'''
        return self.blocks[self.selected_block[self.sub_page]].button_sel_opt()

    def process_user_input(self, id: int, value: int|str = _NONE, button_del: bool = False, button_sel_opt: bool = False) -> bool:
        '''process user input at page level (ui.set_user_input_tuple > ui.user_input_tuple > ui.process_user_input >
        Page/PagesTab.process_user_input); called by ui.process_user_input'''
        return False

    def set_trigger(self) -> None:
        '''set active trigger (triggered by trigger button) at page level; called by ui.set_trigger (also calling router.set_trigger)'''
        pass

    def midi_learn(self, port: int, channel: int, trigger: int, zone: int, note: int, program: int, cc: int, cc_value: int) -> bool:
        '''process midi learn input, save settings and reload options; called by ui.process_midi_learn_data'''
        return False

    def callback_input(self, id: int, value: int|str = _NONE, button_del: bool = False, button_sel_opt: bool = False) -> None:
        '''callback function for encoder input and blocks offering user input (Ui._callback_button/Page/PagesTab.callback_input >
        ui.set_user_input_tuple > ui.user_input_tuple > Ui.process_user_input > Page/PagesTab.process_user_input); called (passed on)
        by self.encoder and Page*._build_sub_page'''
        ml.ui.set_user_input_tuple((self.id, id, value, button_del, button_sel_opt))
    
    def _load(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks; called by self.set_visibility, Page*.program_change, Page*.process_user_input,
        PageProgram.set_trigger and PageMonitor.add_to_monitor'''
        pass

    def _sub_page_selector(self, redraw: bool = True) -> None:
        '''change title bar colour and set encoder range to select sub-page (when page button is pressed); called by self.set_visibility and
         self.set_page_encoders'''
        if len(self.sub_pages_title_bars) <= 1:
            return
        self.title_bar.update(True, redraw)
        ml.ui.encoder_nav.set(self.sub_page, len(self.sub_pages_blocks) - 1)

    def _set_sub_page(self, sub_page: int) -> None:
        '''set sub-page to be visible; called by Page*.process_user_input and Page*._build_page'''
        self.sub_page = sub_page
        self.title_bar = self.sub_pages_title_bars[sub_page]
        self.blocks = self.sub_pages_blocks[sub_page]
        self.empty_blocks = self.sub_pages_empty_blocks[sub_page]
        try:
            self.text_row = self.sub_pages_text_rows[sub_page]
        except:
            self.text_row = None

    def _initiate_nav_encoder(self, value: int = 0) -> None:
        '''initiate navigation encoder to select blocks; called by self._draw and self.set_page_encoders'''
        ml.ui.encoder_nav.set(value, len(self.blocks) - 1)