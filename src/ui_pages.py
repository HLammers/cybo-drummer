''' Library providing base UI page class for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

import ui
if __debug__: import screen_log

_NONE             = const(-1)

_POP_UP_TEXT_EDIT = const(0)

_SELECT_SUB_PAGE  = const(-1)

class Page():
    '''ui page base class'''

    def __init__(self, id: int, x: int, y: int, w: int, h: int, visible: bool) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.visible = visible
        self.selected_block = 0
        self.sub_pages_blocks = []
        self.sub_pages_empty_blocks = []
        self.sub_pages_title_bars = []
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
            if ui.ui.page_pressed:
                self._sub_page_selector()
            elif len(blocks) > 0:
                blocks[0].update(True, False)
            self._load()
        else:
            self.visible = visible

    def program_change(self) -> None:
        '''update page after program change (also needed to trigger draw); called by ui.program_change'''
        pass

    def restore(self):
        '''redraw dynamically changing blocks on page; called by ui.process_user_input'''
        self.title_bar.draw()
        blocks = self.blocks
        if len(blocks) > 0:
            blocks[self.selected_block].update(True, False)
        self._draw()

    def set_page_encoders(self, page_pressed: bool) -> None:
        '''switches value encoder input to or from page selection and changes colour of title bar (when page button is pressed); called by
        ui.process_user_input'''
        blocks = self.blocks
        if page_pressed:
            if len(blocks) > 0:
                blocks[self.selected_block].update(False)
            self._sub_page_selector()
        else:
            self.title_bar.update(False)
            if len(blocks) > 0:
                selected_block = self.selected_block
                blocks[selected_block].update(True, encoder_nr=1)
                self._initiate_navigate_encoder(selected_block)

    def encoder(self, encoder_nr: int, value: int, page_button: bool) -> None:
        '''process encoder input at page level (ui.process_encoder > Page.encoder/PopUp.encoder/PagesTab.set_page > Block: *.encoder);
        called by ui.process_encoder_input'''
        if page_button:
            if len(self.sub_pages_blocks) > 1:
                self.callback_input(_SELECT_SUB_PAGE, value)
            return
        if len(self.blocks) == 0:
            return
        blocks = self.blocks
        selected_block = self.selected_block
        if encoder_nr == 1:
            blocks[selected_block].encoder(value)
        elif value != selected_block:
            blocks[selected_block].update(False)
            self.selected_block = value
            blocks[value].update(True)

    def button_backspace(self) -> None:
        '''process backspace button press at page level; called by ui.process_user_input'''
        self.blocks[self.selected_block].button_backspace()

    def button_select(self) -> None:
        '''process select button press at page level; called by ui.process_user_input'''
        self.blocks[self.selected_block].button_select()

######
    # def button_trigger(self) -> bool:
    #     '''process trigger button press at page level; called by ui.process_user_input'''
    #     return False

    def process_user_input(self, id: int, value: int  = _NONE, text: str = '',
                           button_encoder_0: bool = False, button_encoder_1: bool = False) -> None:
        '''process user input at page level (ui.ui.set_user_input_dict > global user_input_dict > ui.process_user_input >
        Page/PagesTab.process_user_input); called by ui.process_user_input'''
        pass

    def set_trigger(self) -> None:
        '''set active trigger (triggered by trigger button) at page level; called by ui.set_trigger (also calling router.set_trigger)'''
        pass

    def midi_learn(self, port: int, channel: int, note: int, program: int, cc: int, cc_value: int, route_number: int) -> None:
        '''process midi learn input, save settings and reload options; called by ui.process_midi_learn_data'''
        pass

    def callback_input(self, id: int, value: int = _NONE, text: str = '', button_encoder_0: bool = False, button_encoder_1: bool = False) -> None:
        '''callback function for encoder input and blocks offering user input (Ui._callback_button/Page/PagesTab.callback_input > ui.ui.set_user_input_dict >
        global user_input_dict > Ui.process_user_input > Page/PagesTab.process_user_input); called (passed on) by self.encoder and
        Page*._build_sub_page'''
        ui.set_user_input_dict({'frame_id': self.id, 'block_id': id, 'value': value, 'text': text,
                                'button_encoder_0': button_encoder_0, 'button_encoder_1': button_encoder_1, 'frame_select': False})

    def _draw(self) -> None:
        '''draw whole page or only dynamically changing blocks on page; called by self.restore, Page*._load and PageProgram._callback_menu'''
        _ui = ui.ui
        if not self.visible or _ui.active_pop_up is not None:
            return
        page_pressed = _ui.page_pressed
        blocks = self.blocks
        selected_block = self.selected_block
        if len(blocks) > 0:
            blocks[selected_block].update(not page_pressed, False)
        for block in self.empty_blocks:
            block.draw()
        title_bar = self.title_bar
        title_bar.draw()
        for block in blocks:
            block.draw(_ui.page_pressed)
        title_bar.update(page_pressed)
        _text_edit = _ui.pop_ups[_POP_UP_TEXT_EDIT]
        if _text_edit.visible:
            _text_edit.draw()
        elif not page_pressed:
            self._initiate_navigate_encoder(selected_block)

    def _load(self, redraw: bool = True) -> None:
        '''load and set options and values to input blocks; called by self.set_visibility, Page*.program_change, Page*.process_user_input,
        PageProgram.set_trigger and PageMonitor.add_to_monitor'''
        pass

    def _sub_page_selector(self) -> None:
        '''change title bar colour and set encoder range to select sub-page (when page button is pressed); called by self.set_visibility and
         self.set_page_encoders'''
        if len(self.sub_pages_title_bars) <= 1:
            return
        self.title_bar.update(True)
        ui.encoder_0.set(self.sub_page, 0, len(self.sub_pages_blocks) - 1)

    def _set_sub_page(self, sub_page: int) -> None:
        '''set sub-page to be visible; called by Page*.process_user_input and Page*._build_page'''
        if __debug__:
            if self.visible: screen_log.add_marker(f'set sub-page to {sub_page}')
        self.sub_page = sub_page
        self.title_bar = self.sub_pages_title_bars[sub_page]
        self.blocks = self.sub_pages_blocks[sub_page]
        self.empty_blocks = self.sub_pages_empty_blocks[sub_page]
        self.selected_block = 0

    def _initiate_navigate_encoder(self, value: int = 0) -> None:
        '''initiate navigation encoder to select blocks; called by self._draw and self.set_page_encoders'''
        ui.encoder_0.set(value, 0, len(self.blocks) - 1)